from django.db import models
from dirtyfields import DirtyFieldsMixin


class TestModel(DirtyFieldsMixin, models.Model):
    """A simple test model to test dirty fields mixin with"""
    boolean = models.BooleanField(default=True)
    characters = models.CharField(blank=True, max_length=80)


class TestModelWithForeignKey(DirtyFieldsMixin, models.Model):
    fkey = models.ForeignKey(TestModel)


class TestModelWithSelfForeignKey(DirtyFieldsMixin, models.Model):
    fkey = models.ForeignKey("self", blank=True, null=True, on_delete=models.PROTECT)


class TestModelWithOneToOneField(DirtyFieldsMixin, models.Model):
    o2o = models.OneToOneField(TestModel)


class TestModelWithNonEditableFields(DirtyFieldsMixin, models.Model):
    dt = models.DateTimeField(auto_now_add=True)
    characters = models.CharField(blank=True, max_length=80,
                                  editable=False)
    boolean = models.BooleanField(default=True)
