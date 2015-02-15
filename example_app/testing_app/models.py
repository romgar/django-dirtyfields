from django.db import models
from dirtyfields import DirtyFieldsMixin


class TestModel(DirtyFieldsMixin, models.Model):
    """A simple test model to test dirty fields mixin with"""
    boolean = models.BooleanField(default=True)
    characters = models.CharField(blank=True, max_length=80)


class TestModelWithForeignKey(DirtyFieldsMixin, models.Model):
    fkey = models.ForeignKey(TestModel)


class TestModelWithManyToMany(DirtyFieldsMixin, models.Model):
    m2m = models.ManyToManyField(TestModel)
