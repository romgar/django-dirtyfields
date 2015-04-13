# Adapted from http://stackoverflow.com/questions/110803/dirty-fields-in-django

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save


class DirtyFieldsMixin(object):
    def __init__(self, *args, **kwargs):
        super(DirtyFieldsMixin, self).__init__(*args, **kwargs)
        post_save.connect(
            reset_state, sender=self.__class__,
            dispatch_uid='{name}-DirtyFieldsMixin-sweeper'.format(
                name=self.__class__.__name__))
        reset_state(sender=self.__class__, instance=self)

    def _as_dict(self, check_relationship):
        all_field = {}

        for field in self._meta.local_fields:
            if field.rel and not check_relationship:
                continue
            getter = self._get_dirtyfield_getter(field)
            if getter:
                all_field[field.name] = getattr(self, getter)(field)
            else:
                all_field[field.name] = getattr(self, field.name)

        return all_field

    def _get_dirtyfield_getter(self, field):
        cls = field.__class__
        for klass in (cls,) + cls.__bases__:
            getter_name = 'get_{}_dirtyfield'.format(klass.__name__)
            if hasattr(self, getter_name):
                break
        else:
            getter_name = False

        return getter_name

    def get_dirty_fields(self, check_relationship=False):
        # check_relationship indicates whether we want to check for
        # foreign keys and one-to-one fields or ignore them
        new_state = self._as_dict(check_relationship)
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
    # original state should hold all possible dirty fields to avoid
    # getting a `KeyError` when checking if a field is dirty or not
    instance._original_state = instance._as_dict(check_relationship=True)
