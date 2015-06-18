from decimal import Decimal
import pytest

from .models import (TestModel, TestModelWithForeignKey, TestModelWithOneToOneField,
                     SubclassModel, TestModelWithDecimalField)


def test_dirty_fields():
    tm = TestModel()
    # initial state shouldn't be dirty
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

    is_dirty = subclass.is_dirty()
    assert is_dirty is True
    assert subclass.get_dirty_fields() == {'characters': 'foo'}


@pytest.mark.django_db
def test_decimal_field_correctly_managed():
    # Non regression test case for bug:
    # https://github.com/smn/django-dirtyfields/issues/4
    tm = TestModelWithDecimalField.objects.create(decimal_field=Decimal(2.00))

    # initial state shouldn't be dirty
    is_dirty = tm.is_dirty()
    assert is_dirty is False

    tm.decimal_field = 2.0
    # Assigning again to is_dirty because 'assert tm.is_dirty() is False' has not an explicit
    # output in case of errors.
    is_dirty = tm.is_dirty()
    assert is_dirty is False

    tm.decimal_field = u"2.00"
    is_dirty = tm.is_dirty()
    assert is_dirty is False
