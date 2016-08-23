from django.db import models
from django.db.models.signals import pre_save
from django.utils import timezone
from dirtyfields import DirtyFieldsMixin
from dirtyfields.compare import timezone_support_compare


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
    compare_function = (timezone_support_compare, {})
    datetime_field = models.DateTimeField(default=timezone.now)


class TestCurrentDatetimeModel(DirtyFieldsMixin, models.Model):
    compare_function = (timezone_support_compare, {'timezone_to_set': timezone.get_current_timezone()})
    datetime_field = models.DateTimeField(default=timezone.now)


class TestM2MModel(DirtyFieldsMixin, models.Model):
    m2m_field = models.ManyToManyField(TestModel)
    ENABLE_M2M_CHECK = True


class TestM2MModelWithoutM2MModeEnabled(DirtyFieldsMixin, models.Model):
    m2m_field = models.ManyToManyField(TestModel)


class TestModelWithCustomPK(DirtyFieldsMixin, models.Model):
    custom_primary_key = models.CharField(max_length=80, primary_key=True)


class TestM2MModelWithCustomPKOnM2M(DirtyFieldsMixin, models.Model):
    m2m_field = models.ManyToManyField(TestModelWithCustomPK)


class TestModelWithPreSaveSignal(DirtyFieldsMixin, models.Model):
    data = models.CharField(max_length=255)
    data_updated_on_presave = models.CharField(max_length=255, blank=True, null=True)

    @staticmethod
    def pre_save(instance, *args, **kwargs):
        dirty_fields = instance.get_dirty_fields()
        # only works for case2
        if 'data' in dirty_fields:
            if 'specific_value' in instance.data:
                instance.data_updated_on_presave = 'presave_value'

pre_save.connect(TestModelWithPreSaveSignal.pre_save, sender=TestModelWithPreSaveSignal)


class TestModelWithoutM2MCheck(DirtyFieldsMixin, models.Model):
    characters = models.CharField(blank=True, max_length=80)
    ENABLE_M2M_CHECK = False


class TestDoubleForeignKeyModel(DirtyFieldsMixin, models.Model):
    fkey1 = models.ForeignKey(TestModel)
    fkey2 = models.ForeignKey(TestModel, null=True, related_name='fkey2')
