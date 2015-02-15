# Adapted from http://stackoverflow.com/questions/110803/dirty-fields-in-django

from django.db.models.signals import post_save
from django.forms.models import model_to_dict

class DirtyFieldsMixin(object):
    def __init__(self, *args, **kwargs):
        super(DirtyFieldsMixin, self).__init__(*args, **kwargs)
        post_save.connect(
            reset_state, sender=self.__class__,
            dispatch_uid='{name}-DirtyFieldsMixin-sweeper'.format(
                name=self.__class__.__name__))
        reset_state(sender=self.__class__, instance=self)

    def _full_dict(self):
        return model_to_dict(self)

    def _as_dict(self):
        all_field = {}

        for field in self._meta.local_fields:
            if not field.rel:
                all_field[field.name] = getattr(self, field.name)

        return all_field

    def get_dirty_fields(self, check_relationship=False):
        if check_relationship:
            new_state = self._full_dict()
        else:
            new_state = self._as_dict()
        all_modify_field = {}
        # import pdb; pdb.set_trace()
        for key, value in self._original_state.iteritems():
            try:
                if value != new_state[key]:
                    all_modify_field[key] = value
            except KeyError:
                # We are trying to compare a field that is a relationship in the classic mode
                # Skipping it.
                pass

        return all_modify_field

    def is_dirty(self):
        # in order to be dirty we need to have been saved at least once, so we
        # check for a primary key and we need our dirty fields to not be empty
        if not self.pk:
            return True
        return {} != self.get_dirty_fields()


def reset_state(sender, instance, **kwargs):
    # import pdb; pdb.set_trace()
    instance._original_state = instance._full_dict()
