from decimal import Decimal
import pytest

from .models import (TestModel, TestModelWithForeignKey, TestModelWithOneToOneField,
                     SubclassModel, TestModelWithDecimalField)



@pytest.mark.django_db
def test_is_dirty_function():
    tm = TestModel.objects.create()

    # If the object has just been saved in the db, fields are not dirty
    assert tm.get_dirty_fields() == {}
    assert not tm.is_dirty()

    # As soon as we change a field, it becomes dirty
    tm.boolean = False

    assert tm.get_dirty_fields() == {'boolean': True}
    assert tm.is_dirty()


@pytest.mark.django_db
def test_dirty_fields():
    tm = TestModel()

    # Initial state is dirty, so should return all fields
    assert tm.get_dirty_fields() == {'boolean': True, 'characters': ''}

    tm.save()

    # Saving them make them not dirty anymore
    assert tm.get_dirty_fields() == {}

    # Changing values should flag them as dirty again
    tm.boolean = False
    tm.characters = 'testing'

    assert tm.get_dirty_fields() == {
        'boolean': True,
        'characters': ''
    }

    # Resetting them to original values should unflag
    tm.boolean = True
    assert tm.get_dirty_fields() == {
        'characters': ''
    }


@pytest.mark.django_db
def test_dirty_fields_for_notsaved_pk():
    tm = TestModel(id=1)

    # Initial state is dirty, so should return all fields
    assert tm.get_dirty_fields() == {'id': 1, 'boolean': True, 'characters': ''}

    tm.save()

    # Saving them make them not dirty anymore
    assert tm.get_dirty_fields() == {}


@pytest.mark.django_db
def test_relationship_option_for_foreign_key():
    tm1 = TestModel.objects.create()
    tm2 = TestModel.objects.create()
    tm = TestModelWithForeignKey.objects.create(fkey=tm1)

    # Let's change the foreign key value and see what happens
    tm.fkey = tm2

    # Default dirty check is not taking foreign keys into account
    assert tm.get_dirty_fields() == {}

    # But if we use 'check_relationships' param, then foreign keys are compared
    assert tm.get_dirty_fields(check_relationship=True) == {
        'fkey': tm1.pk
    }


@pytest.mark.django_db
def test_relationship_option_for_one_to_one_field():
    tm1 = TestModel.objects.create()
    tm2 = TestModel.objects.create()
    tm = TestModelWithOneToOneField.objects.create(o2o=tm1)

    # Let's change the one to one field and see what happens
    tm.o2o = tm2

    # Default dirty check is not taking onetoone fields into account
    assert tm.get_dirty_fields() == {}

    # But if we use 'check_relationships' param, then one to one fields are compared
    assert tm.get_dirty_fields(check_relationship=True) == {
        'o2o': tm1.pk
    }


@pytest.mark.django_db
def test_non_local_fields():
    subclass = SubclassModel.objects.create(characters='foo')
    subclass.characters = 'spam'

    assert subclass.get_dirty_fields() == {'characters': 'foo'}


@pytest.mark.django_db
def test_decimal_field_correctly_managed():
    # Non regression test case for bug:
    # https://github.com/romgar/django-dirtyfields/issues/4
    tm = TestModelWithDecimalField.objects.create(decimal_field=Decimal(2.00))

    tm.decimal_field = 2.0
    assert tm.get_dirty_fields() == {}

    tm.decimal_field = u"2.00"
    assert tm.get_dirty_fields() == {}


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
    assert tm.get_dirty_fields() == {'boolean': None, 'characters': ''}

    tm.boolean = False
    assert tm.get_dirty_fields() == {'boolean': False, 'characters': ''}


@pytest.mark.django_db
def test_verbose_mode():
    tm = TestModel.objects.create()
    tm.boolean = False

    assert tm.get_dirty_fields(verbose=True) == {
        'boolean': {'saved': True, 'current': False}
    }
