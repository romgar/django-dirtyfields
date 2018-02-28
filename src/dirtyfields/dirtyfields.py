# Adapted from http://stackoverflow.com/questions/110803/dirty-fields-in-django
from copy import deepcopy

from django.core.exceptions import ValidationError
from django.db.models.expressions import BaseExpression
from django.db.models.expressions import Combinable
from django.db.models.signals import post_save, m2m_changed

from .compare import raw_compare, compare_states
from .compat import is_buffer, get_m2m_with_model, remote_field


class DirtyFieldsMixin(object):
    compare_function = (raw_compare, {})

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

    def _connect_m2m_relations(self):
        for m2m_field, model in get_m2m_with_model(self.__class__):
            m2m_changed.connect(
                reset_state, sender=remote_field(m2m_field).through, weak=False,
                dispatch_uid='{name}-DirtyFieldsMixin-sweeper-m2m'.format(
                    name=self.__class__.__name__))

    def _as_dict(self, check_relationship, include_primary_key=True):
        all_field = {}

        deferred_fields = self.get_deferred_fields()

        for field in self._meta.fields:
            if self.FIELDS_TO_CHECK and (field.get_attname() not in self.FIELDS_TO_CHECK):
                continue

            if field.primary_key and not include_primary_key:
                continue

            if remote_field(field):
                if not check_relationship:
                    continue

            if field.get_attname() in deferred_fields:
                continue

            field_value = getattr(self, field.attname)

            # If current field value is an expression, we are not evaluating it
            if isinstance(field_value, (BaseExpression, Combinable)):
                continue

            try:
                # Store the converted value for fields with conversion
                field_value = field.to_python(field_value)
            except ValidationError:
                # The current value is not valid so we cannot convert it
                pass

            if is_buffer(field_value):
                # psycopg2 returns uncopyable type buffer for bytea
                field_value = str(field_value)

            # Explanation of copy usage here :
            # https://github.com/romgar/django-dirtyfields/commit/efd0286db8b874b5d6bd06c9e903b1a0c9cc6b00
            all_field[field.name] = deepcopy(field_value)

        return all_field

    def _as_dict_m2m(self):
        m2m_fields = {}

        if self.pk:
            for f, model in get_m2m_with_model(self.__class__):
                if self.FIELDS_TO_CHECK and (f.attname not in self.FIELDS_TO_CHECK):
                    continue

                m2m_fields[f.attname] = set([obj.pk for obj in getattr(self, f.attname).all()])

        return m2m_fields

    def get_dirty_fields(self, check_relationship=False, check_m2m=None, verbose=False):
        if self._state.adding:
            # If the object has not yet been saved in the database, all fields are considered dirty
            # for consistency (see https://github.com/romgar/django-dirtyfields/issues/65 for more details)
            pk_specified = self.pk is not None
            initial_dict = self._as_dict(check_relationship, include_primary_key=pk_specified)
            if verbose:
                initial_dict = {key: {'saved': None, 'current': value}
                                for key, value in initial_dict.items()}
            return initial_dict

        if check_m2m is not None and not self.ENABLE_M2M_CHECK:
            raise ValueError("You can't check m2m fields if ENABLE_M2M_CHECK is set to False")

        modified_fields = compare_states(self._as_dict(check_relationship),
                                         self._original_state,
                                         self.compare_function)

        if check_m2m:
            modified_m2m_fields = compare_states(check_m2m,
                                                 self._original_m2m_state,
                                                 self.compare_function)
            modified_fields.update(modified_m2m_fields)

        if not verbose:
            # Keeps backward compatibility with previous function return
            modified_fields = {key: value['saved'] for key, value in modified_fields.items()}

        return modified_fields

    def is_dirty(self, check_relationship=False, check_m2m=None):
        return {} != self.get_dirty_fields(check_relationship=check_relationship,
                                           check_m2m=check_m2m)

    def save_dirty_fields(self):
        dirty_fields = self.get_dirty_fields(check_relationship=True)
        self.save(update_fields=dirty_fields.keys())


def reset_state(sender, instance, **kwargs):
    # original state should hold all possible dirty fields to avoid
    # getting a `KeyError` when checking if a field is dirty or not
    update_fields = kwargs.pop('update_fields', {})
    new_state = instance._as_dict(check_relationship=True)
    FIELDS_TO_CHECK = getattr(instance, "FIELDS_TO_CHECK", None)
    if update_fields:
        for field_name in update_fields:
            field = sender._meta.get_field(field_name)
            if not FIELDS_TO_CHECK or \
                    (field.get_attname() in FIELDS_TO_CHECK):

                if field.get_attname() in instance.get_deferred_fields():
                    continue

                instance._original_state[field.name] = new_state[field.name]

    else:
        instance._original_state = new_state
    if instance.ENABLE_M2M_CHECK:
        instance._original_m2m_state = instance._as_dict_m2m()
