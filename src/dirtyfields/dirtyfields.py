# Adapted from http://stackoverflow.com/questions/110803/dirty-fields-in-django
import datetime
from copy import deepcopy

from django.core.exceptions import ValidationError
from django.db.models import DateTimeField, DateField
from django.db.models.expressions import BaseExpression
from django.db.models.expressions import Combinable
from django.db.models.signals import post_save, m2m_changed
from django.utils import timezone

from .compare import raw_compare, compare_states, normalise_value
from .compat import is_buffer

SKIP_FIELD = object()


def get_m2m_with_model(given_model):
    return [
        (f, f.model if f.model != given_model else None)
        for f in given_model._meta.get_fields()
        if f.many_to_many and not f.auto_created
    ]


class DirtyFieldsMixin(object):
    compare_function = (raw_compare, {})
    normalise_function = (normalise_value, {})

    # This mode has been introduced to handle some situations like this one:
    # https://github.com/romgar/django-dirtyfields/issues/73
    ENABLE_M2M_CHECK = False

    FIELDS_TO_CHECK = None

    def __init__(self, *args, **kwargs):
        super(DirtyFieldsMixin, self).__init__(*args, **kwargs)
        post_save.connect(
            reset_state, sender=self.__class__, weak=False,
            dispatch_uid='{name}-DirtyFieldsMixin-sweeper'.format(
                name=self.__class__.__name__))
        if self.ENABLE_M2M_CHECK:
            self._connect_m2m_relations()
        reset_state(sender=self.__class__, instance=self)

    def refresh_from_db(self, using=None, fields=None):
        super(DirtyFieldsMixin, self).refresh_from_db(using=using, fields=fields)
        reset_state(sender=self.__class__, instance=self, update_fields=fields)

    def _connect_m2m_relations(self):
        for m2m_field, model in get_m2m_with_model(self.__class__):
            m2m_changed.connect(
                reset_state, sender=m2m_field.remote_field.through, weak=False,
                dispatch_uid='{name}-DirtyFieldsMixin-sweeper-m2m'.format(
                    name=self.__class__.__name__))

    def _as_dict(self, check_relationship, include_primary_key=True):
        all_field = {}

        deferred_fields = self.get_deferred_fields()

        for field in self._meta.fields:
            field_value = self.__resolve_field_value(field, check_relationship, include_primary_key, deferred_fields)
            if field_value != SKIP_FIELD:
                # Explanation of copy usage here :
                # https://github.com/romgar/django-dirtyfields/commit/efd0286db8b874b5d6bd06c9e903b1a0c9cc6b00
                all_field[field.name] = deepcopy(field_value)

        return all_field

    def __resolve_field_value(self, field, check_relationship=False, include_primary_key=True, deferred_fields=tuple()):
        # For backward compatibility reasons, in particular for fkey fields, we check both
        # the real name and the wrapped name (it means that we can specify either the field
        # name with or without the "_id" suffix.
        field_names_to_check = [field.name, field.get_attname()]
        if self.FIELDS_TO_CHECK and (not any(name in self.FIELDS_TO_CHECK for name in field_names_to_check)):
            return SKIP_FIELD

        if field.primary_key and not include_primary_key:
            return SKIP_FIELD

        if field.remote_field:
            if not check_relationship:
                return SKIP_FIELD

        if field.get_attname() in deferred_fields:
            return SKIP_FIELD

        field_value = getattr(self, field.attname)

        # If current field value is an expression, we are not evaluating it
        if isinstance(field_value, (BaseExpression, Combinable)):
            return SKIP_FIELD

        try:
            # Store the converted value for fields with conversion
            field_value = field.to_python(field_value)
        except ValidationError:
            # The current value is not valid so we cannot convert it
            pass

        if is_buffer(field_value):
            # psycopg2 returns uncopyable type buffer for bytea
            field_value = bytes(field_value)

        return field_value

    def _as_dict_m2m(self):
        m2m_fields = {}

        if self.pk:
            for f, model in get_m2m_with_model(self.__class__):
                if self.FIELDS_TO_CHECK and (f.attname not in self.FIELDS_TO_CHECK):
                    continue

                m2m_fields[f.attname] = set([obj.pk for obj in getattr(self, f.attname).all()])

        return m2m_fields

    def get_dirty_fields(self, check_relationship=False, check_m2m=None, verbose=False, include_auto_now=False):
        if self._state.adding:
            # If the object has not yet been saved in the database, all fields are considered dirty
            # for consistency (see https://github.com/romgar/django-dirtyfields/issues/65 for more details)
            pk_specified = self.pk is not None
            initial_dict = self._as_dict(check_relationship, include_primary_key=pk_specified)
            if verbose:
                initial_dict = {key: {'saved': None, 'current': self.normalise_function[0](value)}
                                for key, value in initial_dict.items()}
            return initial_dict

        if check_m2m is not None and not self.ENABLE_M2M_CHECK:
            raise ValueError("You can't check m2m fields if ENABLE_M2M_CHECK is set to False")

        modified_fields = compare_states(self._as_dict(check_relationship),
                                         self._original_state,
                                         self.compare_function,
                                         self.normalise_function)

        if check_m2m:
            modified_m2m_fields = compare_states(check_m2m,
                                                 self._original_m2m_state,
                                                 self.compare_function,
                                                 self.normalise_function)
            modified_fields.update(modified_m2m_fields)

        if modified_fields and include_auto_now:
            auto_add_fields = {}
            relevant_datetime_fields = filter(
                lambda value: isinstance(value, (DateTimeField, DateField)) and value.auto_now,
                self._meta.fields
            )
            for field in relevant_datetime_fields:
                field_value = self.__resolve_field_value(field)
                if field_value == SKIP_FIELD:
                    continue
                current_value = None
                if isinstance(field, DateTimeField):
                    current_value = timezone.now()
                elif isinstance(field, DateField):
                    current_value = datetime.date.today()
                auto_add_fields[field.name] = {"saved": field_value, "current": current_value}
            modified_fields.update(auto_add_fields)

        if not verbose:
            # Keeps backward compatibility with previous function return
            modified_fields = {key: self.normalise_function[0](value['saved']) for key, value in modified_fields.items()}

        return modified_fields

    def is_dirty(self, check_relationship=False, check_m2m=None):
        return {} != self.get_dirty_fields(check_relationship=check_relationship,
                                           check_m2m=check_m2m)

    def save_dirty_fields(self, include_auto_now=False):
        dirty_fields = self.get_dirty_fields(check_relationship=True, include_auto_now=include_auto_now)
        self.save(update_fields=dirty_fields.keys())


def reset_state(sender, instance, **kwargs):
    # original state should hold all possible dirty fields to avoid
    # getting a `KeyError` when checking if a field is dirty or not
    update_fields = kwargs.pop('update_fields', None)
    new_state = instance._as_dict(check_relationship=True)
    FIELDS_TO_CHECK = getattr(instance, "FIELDS_TO_CHECK", None)

    if update_fields is not None:
        for field_name in update_fields:
            field = sender._meta.get_field(field_name)
            if not FIELDS_TO_CHECK or (field.name in FIELDS_TO_CHECK):

                if field.get_attname() in instance.get_deferred_fields():
                    continue

                instance._original_state[field.name] = new_state[field.name]
    else:
        instance._original_state = new_state

    if instance.ENABLE_M2M_CHECK:
        instance._original_m2m_state = instance._as_dict_m2m()
