import pytest
from django.db import IntegrityError
from django.test.utils import override_settings

from .models import (ModelTest, ModelWithForeignKeyTest, ModelWithNonEditableFieldsTest,
                     OrdinaryModelTest, OrdinaryModelWithForeignKeyTest, ModelWithSelfForeignKeyTest,
                     ExpressionModelTest, WithPreSaveSignalModelTest, DoubleForeignKeyModelTest,
                     BinaryModelTest)
from .utils import assert_select_number_queries_on_model


@pytest.mark.django_db
def test_slicing_and_only():
    # test for bug: https://github.com/depop/django-dirtyfields/issues/1
    for _ in range(10):
        ModelWithNonEditableFieldsTest.objects.create()

    qs_ = ModelWithNonEditableFieldsTest.objects.only('pk').filter()
    [o for o in qs_.filter().order_by('pk')]


@pytest.mark.django_db
def test_dirty_fields_ignores_the_editable_property_of_fields():
    # Non regression test case for bug:
    # https://github.com/romgar/django-dirtyfields/issues/17
    tm = ModelWithNonEditableFieldsTest.objects.create()

    # Changing values should flag them as dirty
    tm.boolean = False
    tm.characters = 'testing'
    assert tm.get_dirty_fields() == {
        'boolean': True,
        'characters': ''
    }


@pytest.mark.django_db
def test_mandatory_foreign_key_field_not_initialized_is_not_raising_related_object_exception():
    # Non regression test case for bug:
    # https://github.com/romgar/django-dirtyfields/issues/26
    with pytest.raises(IntegrityError):
        ModelWithForeignKeyTest.objects.create()


@pytest.mark.django_db
@override_settings(DEBUG=True)  # The test runner sets DEBUG to False. Set to True to enable SQL logging.
def test_relationship_model_loading_issue():
    # Non regression test case for bug:
    # https://github.com/romgar/django-dirtyfields/issues/34

    # Query tests with models that are not using django-dirtyfields
    tm1 = OrdinaryModelTest.objects.create()
    tm2 = OrdinaryModelTest.objects.create()
    OrdinaryModelWithForeignKeyTest.objects.create(fkey=tm1)
    OrdinaryModelWithForeignKeyTest.objects.create(fkey=tm2)

    with assert_select_number_queries_on_model(OrdinaryModelWithForeignKeyTest, 1):
        with assert_select_number_queries_on_model(OrdinaryModelTest, 0):  # should be 0 since we don't access the relationship for now
            for tmf in OrdinaryModelWithForeignKeyTest.objects.all():
                tmf.pk

    with assert_select_number_queries_on_model(OrdinaryModelWithForeignKeyTest, 1):
        with assert_select_number_queries_on_model(OrdinaryModelTest, 2):
            for tmf in OrdinaryModelWithForeignKeyTest.objects.all():
                tmf.fkey  # access the relationship here

    with assert_select_number_queries_on_model(OrdinaryModelWithForeignKeyTest, 1):
        with assert_select_number_queries_on_model(OrdinaryModelTest, 0):  # should be 0 since we use `select_related`
            for tmf in OrdinaryModelWithForeignKeyTest.objects.select_related('fkey').all():
                tmf.fkey  # access the relationship here

    # Query tests with models that are using django-dirtyfields
    tm1 = ModelTest.objects.create()
    tm2 = ModelTest.objects.create()
    ModelWithForeignKeyTest.objects.create(fkey=tm1)
    ModelWithForeignKeyTest.objects.create(fkey=tm2)

    with assert_select_number_queries_on_model(ModelWithForeignKeyTest, 1):
        with assert_select_number_queries_on_model(ModelTest, 0):  # should be 0, was 2 before bug fixing
            for tmf in ModelWithForeignKeyTest.objects.all():
                tmf.pk  # we don't need the relationship here

    with assert_select_number_queries_on_model(ModelWithForeignKeyTest, 1):
        with assert_select_number_queries_on_model(ModelTest, 2):
            for tmf in ModelWithForeignKeyTest.objects.all():
                tmf.fkey  # access the relationship here

    with assert_select_number_queries_on_model(ModelWithForeignKeyTest, 1):
        with assert_select_number_queries_on_model(ModelTest, 0):  # should be 0 since we use `selected_related` (was 2 before)
            for tmf in ModelWithForeignKeyTest.objects.select_related('fkey').all():
                tmf.fkey  # access the relationship here


@pytest.mark.django_db
def test_relationship_option_for_foreign_key_to_self():
    # Non regression test case for bug:
    # https://github.com/romgar/django-dirtyfields/issues/22
    tm = ModelWithSelfForeignKeyTest.objects.create()
    tm1 = ModelWithSelfForeignKeyTest.objects.create(fkey=tm)

    tm.fkey = tm1
    tm.save()

    # Trying to access an instance was triggering a "RuntimeError: maximum recursion depth exceeded"
    ModelWithSelfForeignKeyTest.objects.all()[0]


@pytest.mark.django_db
def test_expressions_not_taken_into_account_for_dirty_check():
    # Non regression test case for bug:
    # https://github.com/romgar/django-dirtyfields/issues/39
    from django.db.models import F
    tm = ExpressionModelTest.objects.create()
    tm.counter = F('counter') + 1

    # This save() was raising a ValidationError: [u"'F(counter) + Value(1)' value must be an integer."]
    # caused by a call to_python() on an expression node
    tm.save()


@pytest.mark.django_db
def test_pre_save_signal_make_dirty_checking_not_consistent():

    # first case
    model = WithPreSaveSignalModelTest.objects.create(data='specific_value')
    assert model.data_updated_on_presave == 'presave_value'

    # second case
    model = WithPreSaveSignalModelTest(data='specific_value')
    model.save()
    assert model.data_updated_on_presave == 'presave_value'

    # third case
    model = WithPreSaveSignalModelTest()
    model.data = 'specific_value'
    model.save()
    assert model.data_updated_on_presave == 'presave_value'


@pytest.mark.django_db
def test_foreign_key_deferred_field():
    # Non regression test case for bug:
    # https://github.com/romgar/django-dirtyfields/issues/84
    tm = ModelTest.objects.create()
    DoubleForeignKeyModelTest.objects.create(fkey1=tm)

    list(DoubleForeignKeyModelTest.objects.only('fkey1'))  # RuntimeError was raised here!


@pytest.mark.django_db
def test_bytea():
    BinaryModelTest.objects.create(bytea=b'^H\xc3\xabllo')
    tbm = BinaryModelTest.objects.get()
    tbm.bytea = b'W\xc3\xb6rlD'
    assert tbm.get_dirty_fields() == {
        'bytea': b'^H\xc3\xabllo',
    }


@pytest.mark.django_db
def test_access_deferred_field_doesnt_reset_state():
    # Non regression test case for bug:
    # https://github.com/romgar/django-dirtyfields/issues/154
    tm = ModelTest.objects.create(characters="old value")
    tm_deferred = ModelTest.objects.defer("characters").get(id=tm.id)
    assert tm_deferred.get_deferred_fields() == {"characters"}
    tm_deferred.boolean = False
    assert tm_deferred.get_dirty_fields() == {"boolean": True}

    tm_deferred.characters  # access deferred field
    assert tm_deferred.get_deferred_fields() == set()
    # previously accessing the deferred field would reset the dirty state.
    assert tm_deferred.get_dirty_fields() == {"boolean": True}
