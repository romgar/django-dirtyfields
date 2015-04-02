# Adapted from http://stackoverflow.com/questions/110803/dirty-fields-in-django
from django.db.models.signals import post_save


class DirtyFieldsMixin(object):
    def __init__(self, *args, **kwargs):
        super(DirtyFieldsMixin, self).__init__(*args, **kwargs)
        post_save.connect(
            reset_state, sender=self.__class__,
            dispatch_uid='{name}-DirtyFieldsMixin-sweeper'.format(
                name=self.__class__.__name__))
        reset_state(sender=self.__class__, instance=self)

    def _full_dict(self):
        # This function is not factorised with _as_dict() because we want to keep
        # previous behaviour (without check_relationship) untouched, as we want to
        # minimize side-effects that we could have if we regroup full_dict and as_dict.
        all_field = {}

        for field in self._meta.concrete_fields:
            all_field[field.name] = getattr(self, field.name)

        return all_field

    def _as_dict(self):
        all_field = {}

        for field in self._meta.local_fields:
            if not field.rel:
                all_field[field.name] = getattr(self, field.name)

        return all_field

    def get_dirty_fields(self, check_relationship=False):
        if check_relationship:
            # We want to check every field, including foreign keys and
            # one-to-one fields,
            new_state = self._full_dict()
        else:
            new_state = self._as_dict()
        all_modify_field = {}

        for key, value in new_state.iteritems():
            original_value = self._original_state[key]
            if value != original_value:
                all_modify_field[key] = original_value

        return all_modify_field

    def is_dirty(self, check_relationship=False):
        # in order to be dirty we need to have been saved at least once, so we
        # check for a primary key and we need our dirty fields to not be empty
        if not self.pk:
            return True
        return {} != self.get_dirty_fields(check_relationship=check_relationship)


def reset_state(sender, instance, **kwargs):
    instance._original_state = instance._full_dict()
