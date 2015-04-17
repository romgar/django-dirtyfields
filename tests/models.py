from django.db import models
from src.dirtyfields.dirtyfields import DirtyFieldsMixin


class MyForeignKey(models.ForeignKey):
    pass


class TestModel(DirtyFieldsMixin, models.Model):
    """A simple test model to test dirty fields mixin with"""
    boolean = models.BooleanField(default=True)
    characters = models.CharField(blank=True, max_length=80)


class TestModelWithForeignKey(DirtyFieldsMixin, models.Model):
    fkey = models.ForeignKey(TestModel)


class TestModelWithCustomForeignKey(DirtyFieldsMixin, models.Model):
    fkey = MyForeignKey(TestModel)

    def get_MyForeignKey_dirtyfield(self, field):
        return 'foo'


class TestModelWithOneToOneField(DirtyFieldsMixin, models.Model):
    o2o = models.OneToOneField(TestModel)


class TestModelWithManyToManyField(DirtyFieldsMixin, models.Model):
    m2m = models.ManyToManyField(TestModel)


class TestModelWithNonEditableFields(DirtyFieldsMixin, models.Model):
    dt = models.DateTimeField(auto_now_add=True)
    characters = models.CharField(blank=True, max_length=80,
                                  editable=False)
    boolean = models.BooleanField(default=True)
