from django.db import models
from django.utils import timezone
from dirtyfields import DirtyFieldsMixin
from dirtyfields.compare import time_zone_support_compare


class TestModel(DirtyFieldsMixin, models.Model):
    """A simple test model to test dirty fields mixin with"""
    boolean = models.BooleanField(default=True)
    characters = models.CharField(blank=True, max_length=80)


class TestModelWithDecimalField(DirtyFieldsMixin, models.Model):
    decimal_field = models.DecimalField(decimal_places=2, max_digits=10)


class TestModelWithForeignKey(DirtyFieldsMixin, models.Model):
    fkey = models.ForeignKey(TestModel)


class TestMixedFieldsModel(DirtyFieldsMixin, models.Model):
    fkey = models.ForeignKey(TestModel)
    characters = models.CharField(blank=True, max_length=80)


class TestModelWithOneToOneField(DirtyFieldsMixin, models.Model):
    o2o = models.OneToOneField(TestModel)


class TestModelWithNonEditableFields(DirtyFieldsMixin, models.Model):
    dt = models.DateTimeField(auto_now_add=True)
    characters = models.CharField(blank=True, max_length=80,
                                  editable=False)
    boolean = models.BooleanField(default=True)


class TestModelWithSelfForeignKey(DirtyFieldsMixin, models.Model):
    fkey = models.ForeignKey("self", blank=True, null=True)


class OrdinaryTestModel(models.Model):
    boolean = models.BooleanField(default=True)
    characters = models.CharField(blank=True, max_length=80)


class OrdinaryTestModelWithForeignKey(models.Model):
    fkey = models.ForeignKey(OrdinaryTestModel)


class SubclassModel(TestModel):
    pass


class TestExpressionModel(DirtyFieldsMixin, models.Model):
    counter = models.IntegerField(default=0)


class TestDatetimeModel(DirtyFieldsMixin, models.Model):
    compare_function = time_zone_support_compare
    datetime_field = models.DateTimeField(default=timezone.now)
