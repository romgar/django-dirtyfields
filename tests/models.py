from django.db import models
from django.db.models.signals import pre_save
from django.utils import timezone
from jsonfield import JSONField as JSONFieldThirdParty

from dirtyfields import DirtyFieldsMixin
from dirtyfields.compare import timezone_support_compare
from tests.utils import is_postgresql_env_with_jsonb_field


class ModelTest(DirtyFieldsMixin, models.Model):
    """A simple test model to test dirty fields mixin with"""
    boolean = models.BooleanField(default=True)
    characters = models.CharField(blank=True, max_length=80)


class ModelWithDecimalFieldTest(DirtyFieldsMixin, models.Model):
    decimal_field = models.DecimalField(decimal_places=2, max_digits=10)


class ModelWithForeignKeyTest(DirtyFieldsMixin, models.Model):
    fkey = models.ForeignKey(ModelTest, on_delete=models.CASCADE)


class MixedFieldsModelTest(DirtyFieldsMixin, models.Model):
    fkey = models.ForeignKey(ModelTest, on_delete=models.CASCADE)
    characters = models.CharField(blank=True, max_length=80)


class ModelWithOneToOneFieldTest(DirtyFieldsMixin, models.Model):
    o2o = models.OneToOneField(ModelTest, on_delete=models.CASCADE)


class ModelWithNonEditableFieldsTest(DirtyFieldsMixin, models.Model):
    dt = models.DateTimeField(auto_now_add=True)
    characters = models.CharField(blank=True, max_length=80,
                                  editable=False)
    boolean = models.BooleanField(default=True)


class ModelWithSelfForeignKeyTest(DirtyFieldsMixin, models.Model):
    fkey = models.ForeignKey("self", blank=True, null=True, on_delete=models.CASCADE)


class OrdinaryModelTest(models.Model):
    boolean = models.BooleanField(default=True)
    characters = models.CharField(blank=True, max_length=80)


class OrdinaryModelWithForeignKeyTest(models.Model):
    fkey = models.ForeignKey(OrdinaryModelTest, on_delete=models.CASCADE)


class SubclassModelTest(ModelTest):
    pass


class ExpressionModelTest(DirtyFieldsMixin, models.Model):
    counter = models.IntegerField(default=0)


class DatetimeModelTest(DirtyFieldsMixin, models.Model):
    compare_function = (timezone_support_compare, {})
    datetime_field = models.DateTimeField(default=timezone.now)


class CurrentDatetimeModelTest(DirtyFieldsMixin, models.Model):
    compare_function = (timezone_support_compare, {'timezone_to_set': timezone.get_current_timezone()})
    datetime_field = models.DateTimeField(default=timezone.now)


class Many2ManyModelTest(DirtyFieldsMixin, models.Model):
    m2m_field = models.ManyToManyField(ModelTest)
    ENABLE_M2M_CHECK = True


class Many2ManyWithoutMany2ManyModeEnabledModelTest(DirtyFieldsMixin, models.Model):
    m2m_field = models.ManyToManyField(ModelTest)


class ModelWithCustomPKTest(DirtyFieldsMixin, models.Model):
    custom_primary_key = models.CharField(max_length=80, primary_key=True)


class M2MModelWithCustomPKOnM2MTest(DirtyFieldsMixin, models.Model):
    m2m_field = models.ManyToManyField(ModelWithCustomPKTest)


class WithPreSaveSignalModelTest(DirtyFieldsMixin, models.Model):
    data = models.CharField(max_length=255)
    data_updated_on_presave = models.CharField(max_length=255, blank=True, null=True)

    @staticmethod
    def pre_save(instance, *args, **kwargs):
        dirty_fields = instance.get_dirty_fields()
        # only works for case2
        if 'data' in dirty_fields:
            if 'specific_value' in instance.data:
                instance.data_updated_on_presave = 'presave_value'


pre_save.connect(
    WithPreSaveSignalModelTest.pre_save,
    sender=WithPreSaveSignalModelTest,
    dispatch_uid="WithPreSaveSignalModelTest__pre_save",
)


class ModelWithoutM2MCheckTest(DirtyFieldsMixin, models.Model):
    characters = models.CharField(blank=True, max_length=80)
    ENABLE_M2M_CHECK = False


class DoubleForeignKeyModelTest(DirtyFieldsMixin, models.Model):
    fkey1 = models.ForeignKey(ModelTest, on_delete=models.CASCADE)
    fkey2 = models.ForeignKey(ModelTest, null=True, related_name='fkey2',
                              on_delete=models.CASCADE)


if is_postgresql_env_with_jsonb_field():
    from django.contrib.postgres.fields import JSONField as JSONBField

    class ModelWithJSONBFieldTest(DirtyFieldsMixin, models.Model):
        jsonb_field = JSONBField()


class ModelWithJSONFieldThirdPartyTest(DirtyFieldsMixin, models.Model):
    json_field_third_party = JSONFieldThirdParty()


class ModelWithSpecifiedFieldsTest(DirtyFieldsMixin, models.Model):
    boolean1 = models.BooleanField(default=True)
    boolean2 = models.BooleanField(default=True)
    FIELDS_TO_CHECK = ['boolean1']


class ModelWithSpecifiedFieldsAndForeignKeyTest(DirtyFieldsMixin, models.Model):
    boolean1 = models.BooleanField(default=True)
    boolean2 = models.BooleanField(default=True)
    fk_field = models.OneToOneField(ModelTest, null=True,
                                    on_delete=models.CASCADE)
    FIELDS_TO_CHECK = ['fk_field']


class ModelWithSpecifiedFieldsAndForeignKeyTest2(ModelWithSpecifiedFieldsAndForeignKeyTest):
    FIELDS_TO_CHECK = ['fk_field_id']


class ModelWithM2MAndSpecifiedFieldsTest(DirtyFieldsMixin, models.Model):
    m2m1 = models.ManyToManyField(ModelTest)
    m2m2 = models.ManyToManyField(ModelTest)
    ENABLE_M2M_CHECK = True
    FIELDS_TO_CHECK = ['m2m1']


class BinaryModelTest(DirtyFieldsMixin, models.Model):
    bytea = models.BinaryField()
