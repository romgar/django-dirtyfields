from datetime import datetime
from decimal import Decimal
import pytest
import pytz
from django.test.utils import override_settings

from .models import (TestModel, TestModelWithForeignKey, TestModelWithOneToOneField,
                     SubclassModel, TestModelWithDecimalField, TestDatetimeModel)


def test_dirty_fields():
    tm = TestModel()

    # initial state is dirty because it has not been saved yet in the db
    assert tm.is_dirty()
    assert tm.get_dirty_fields() == {}

    # changing values should flag them as dirty
    tm.boolean = False
    tm.characters = 'testing'
    assert tm.get_dirty_fields() == {
        'boolean': True,
        'characters': ''
    }

    # resetting them to original values should unflag
    tm.boolean = True
    assert tm.get_dirty_fields() == {
        'characters': ''
    }


@pytest.mark.django_db
def test_sweeping():
    tm = TestModel()
    tm.boolean = False
    tm.characters = 'testing'
    assert tm.get_dirty_fields() == {
        'boolean': True,
        'characters': ''
    }
    tm.save()
    assert tm.get_dirty_fields() == {}


@pytest.mark.django_db
def test_relationship_option_for_foreign_key():
    tm1 = TestModel.objects.create()
    tm2 = TestModel.objects.create()
    tm = TestModelWithForeignKey.objects.create(fkey=tm1)

    # initial state shouldn't be dirty
    assert tm.get_dirty_fields() == {}

    # Default dirty check is not taking foreign keys into account
    tm.fkey = tm2
    assert tm.get_dirty_fields() == {}

    # But if we use 'check_relationships' param, then we have to.
    assert tm.get_dirty_fields(check_relationship=True) == {
        'fkey': tm1.pk
    }


@pytest.mark.django_db
def test_relationship_option_for_one_to_one_field():
    tm1 = TestModel.objects.create()
    tm2 = TestModel.objects.create()
    tm = TestModelWithOneToOneField.objects.create(o2o=tm1)

    # initial state shouldn't be dirty
    assert tm.get_dirty_fields() == {}

    # Default dirty check is not taking onetoone fields into account
    tm.o2o = tm2
    assert tm.get_dirty_fields() == {}

    # But if we use 'check_relationships' param, then we have to.
    assert tm.get_dirty_fields(check_relationship=True) == {
        'o2o': tm1.pk
    }


@pytest.mark.django_db
def test_non_local_fields():
    subclass = SubclassModel.objects.create(characters='foo')
    subclass.characters = 'spam'

    assert subclass.is_dirty()
    assert subclass.get_dirty_fields() == {'characters': 'foo'}



@pytest.mark.django_db
def test_decimal_field_correctly_managed():
    # Non regression test case for bug:
    # https://github.com/romgar/django-dirtyfields/issues/4
    tm = TestModelWithDecimalField.objects.create(decimal_field=Decimal(2.00))

    # initial state shouldn't be dirty
    assert not tm.is_dirty()

    tm.decimal_field = 2.0
    assert not tm.is_dirty()

    tm.decimal_field = u"2.00"
    assert not tm.is_dirty()


@pytest.mark.django_db
def test_deferred_fields():
    TestModel.objects.create()

    qs = TestModel.objects.only('boolean')

    tm = qs[0]
    tm.boolean = False
    assert tm.get_dirty_fields() == {'boolean': True}

    tm.characters = 'foo'
    # 'characters' is not tracked as it is deferred
    assert tm.get_dirty_fields() == {'boolean': True}


def test_validationerror():
    # Initialize the model with an invalid value
    tm = TestModel(boolean=None)

    # Should not raise ValidationError
    assert tm.is_dirty() is True

    tm.boolean = False
    assert tm.get_dirty_fields() == {'boolean': None}


@override_settings(USE_TZ=True, TIME_ZONE='America/Chicago')
@pytest.mark.django_db
def test_datetime_fields_when_aware_db_and_naive_current_value():
    tm = TestDatetimeModel.objects.create(datetime_field=datetime(2000, 1, 1, tzinfo=pytz.utc))

    # initial state shouldn't be dirty
    assert not tm.is_dirty()

    # Adding a naive datetime
    tm.datetime_field = datetime(2016, 1, 1)

    # 'characters' is not tracked as it is deferred
    assert tm.get_dirty_fields() == {'datetime_field': datetime(2000, 1, 1, tzinfo=pytz.utc)}


@override_settings(USE_TZ=False)
@pytest.mark.django_db
def test_datetime_fields_when_naive_db_and_aware_current_value():

    tm = TestDatetimeModel.objects.create(datetime_field=datetime(2000, 1, 1))

    # initial state shouldn't be dirty
    assert not tm.is_dirty()

    # Adding a naive datetime
    tm.datetime_field = datetime(2016, 1, 1, tzinfo=pytz.utc)

    # 'characters' is not tracked as it is deferred
    assert tm.get_dirty_fields() == {'datetime_field': datetime(2000, 1, 1)}
