# Adapted from http://stackoverflow.com/questions/110803/dirty-fields-in-django
from django.db.models.signals import post_save
from django.db import models

class DirtyFieldsMixin(object):
    def __init__(self, *args, **kwargs):
        super(DirtyFieldsMixin, self).__init__(*args, **kwargs)
        post_save.connect(reset_state, sender=self.__class__,
                            dispatch_uid='%s-DirtyFieldsMixin-sweeper' % self.__class__.__name__)
        reset_state(sender=self.__class__, instance=self)

    def _as_dict(self):
        object_dict = {}
        for f in self._meta.fields:
            is_fk = isinstance(f, models.fields.related.ForeignKey) and not isinstance(f, models.fields.related.OneToOneField)
            if not f.rel or is_fk:
                if is_fk:
                    object_dict[f.attname] = getattr(self, f.attname)
                else:
                    object_dict[f.name] = getattr(self, f.name)

        return object_dict

    def get_dirty_fields(self):
        new_state = self._as_dict()
        return dict([(key, value) for key, value in self._original_state.iteritems() if value != new_state[key]])

    def is_dirty(self):
        # in order to be dirty we need to have been saved at least once, so we
        # check for a primary key and we need our dirty fields to not be empty
        if not self.pk:
            return True
        return {} != self.get_dirty_fields()

def reset_state(sender, instance, **kwargs):
    instance._original_state = instance._as_dict()
