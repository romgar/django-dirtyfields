# Adapted from http://stackoverflow.com/questions/110803/dirty-fields-in-django
from copy import deepcopy

from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, m2m_changed

from .compare import raw_compare, compare_states
from .compat import (is_db_expression, save_specific_fields,
                     is_deferred, is_buffer, get_m2m_with_model, remote_field)


class DirtyFieldsMixin(object):
    compare_function = (raw_compare, {})

    # This mode has been introduced to handle some situations like this one:
    # https://github.com/romgar/django-dirtyfields/issues/73
    ENABLE_M2M_CHECK = False

    def __init__(self, *args, **kwargs):
        super(DirtyFieldsMixin, self).__init__(*args, **kwargs)
        post_save.connect(
            reset_state, sender=self.__class__,
            dispatch_uid='{name}-DirtyFieldsMixin-sweeper'.format(
                name=self.__class__.__name__))
        if self.ENABLE_M2M_CHECK:
            self._connect_m2m_relations()
        reset_state(sender=self.__class__, instance=self)

    def _connect_m2m_relations(self):
        for m2m_field, model in get_m2m_with_model(self.__class__):
            m2m_changed.connect(
                reset_state, sender=remote_field(m2m_field).through,
                dispatch_uid='{name}-DirtyFieldsMixin-sweeper-m2m'.format(
                    name=self.__class__.__name__))

    def _as_dict(self, check_relationship, include_primary_key=True):
        all_field = {}

        for field in self._meta.fields:
            if field.primary_key and not include_primary_key:
                continue

            if remote_field(field):
                if not check_relationship:
                    continue

            if is_deferred(self, field):
                continue

            field_value = getattr(self, field.attname)

            # If current field value is an expression, we are not evaluating it
            if is_db_expression(field_value):
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
        if self.pk:
            m2m_fields = dict([
                (f.attname, set([
                    obj.pk for obj in getattr(self, f.attname).all()
                ]))
                for f, model in get_m2m_with_model(self.__class__)
            ])
            return m2m_fields
        return {}

    def get_dirty_fields(self, check_relationship=False, check_m2m=None, verbose=False):
        if self._state.adding:
            # If the object has not yet been saved in the database, all fields are considered dirty
            # for consistency (see https://github.com/romgar/django-dirtyfields/issues/65 for more details)
            pk_specified = self.pk is not None
            initial_dict = self._as_dict(check_relationship, include_primary_key=pk_specified)
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
        save_specific_fields(self, dirty_fields)


def reset_state(sender, instance, **kwargs):
    # original state should hold all possible dirty fields to avoid
    # getting a `KeyError` when checking if a field is dirty or not
    update_fields = kwargs.pop('update_fields', {})
    new_state = instance._as_dict(check_relationship=True)
    if update_fields:
        for field in update_fields:
            instance._original_state[field] = new_state[field]
    else:
        instance._original_state = new_state
    if instance.ENABLE_M2M_CHECK:
        instance._original_m2m_state = instance._as_dict_m2m()
