from decimal import Decimal
from os.path import dirname, join

import pytest
from django.core.files.base import ContentFile, File

import dirtyfields
from .models import (ModelTest, ModelWithForeignKeyTest,
                     ModelWithOneToOneFieldTest,
                     SubclassModelTest, ModelWithDecimalFieldTest,
                     FileFieldModel)
from .utils import FakeFieldFile


def test_version_numbers():
    assert isinstance(dirtyfields.__version__, str)
    assert isinstance(dirtyfields.VERSION, tuple)
    assert all(isinstance(number, int) for number in dirtyfields.VERSION)


@pytest.mark.django_db
def test_is_dirty_function():
    tm = ModelTest.objects.create()

    # If the object has just been saved in the db, fields are not dirty
    assert tm.get_dirty_fields() == {}
    assert not tm.is_dirty()

    # As soon as we change a field, it becomes dirty
    tm.boolean = False

    assert tm.get_dirty_fields() == {'boolean': True}
    assert tm.is_dirty()


@pytest.mark.django_db
def test_dirty_fields():
    tm = ModelTest()

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
    tm = ModelTest(id=1)

    # Initial state is dirty, so should return all fields
    assert tm.get_dirty_fields() == {'id': 1, 'boolean': True, 'characters': ''}

    tm.save()

    # Saving them make them not dirty anymore
    assert tm.get_dirty_fields() == {}


@pytest.mark.django_db
def test_relationship_option_for_foreign_key():
    tm1 = ModelTest.objects.create()
    tm2 = ModelTest.objects.create()
    tm = ModelWithForeignKeyTest.objects.create(fkey=tm1)

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
    tm1 = ModelTest.objects.create()
    tm2 = ModelTest.objects.create()
    tm = ModelWithOneToOneFieldTest.objects.create(o2o=tm1)

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
    subclass = SubclassModelTest.objects.create(characters='foo')
    subclass.characters = 'spam'

    assert subclass.get_dirty_fields() == {'characters': 'foo'}


@pytest.mark.django_db
def test_decimal_field_correctly_managed():
    # Non regression test case for bug:
    # https://github.com/romgar/django-dirtyfields/issues/4
    tm = ModelWithDecimalFieldTest.objects.create(decimal_field=Decimal(2.00))

    tm.decimal_field = 2.0
    assert tm.get_dirty_fields() == {}

    tm.decimal_field = u"2.00"
    assert tm.get_dirty_fields() == {}


@pytest.mark.django_db
def test_deferred_fields():
    ModelTest.objects.create()

    qs = ModelTest.objects.only('boolean')

    tm = qs[0]
    tm.boolean = False
    assert tm.get_dirty_fields() == {'boolean': True}

    tm.characters = 'foo'
    # 'characters' is not tracked as it is deferred
    assert tm.get_dirty_fields() == {'boolean': True}


def test_validationerror():
    # Initialize the model with an invalid value
    tm = ModelTest(boolean=None)

    # Should not raise ValidationError
    assert tm.get_dirty_fields() == {'boolean': None, 'characters': ''}

    tm.boolean = False
    assert tm.get_dirty_fields() == {'boolean': False, 'characters': ''}


@pytest.mark.django_db
def test_verbose_mode():
    tm = ModelTest.objects.create()
    tm.boolean = False

    assert tm.get_dirty_fields(verbose=True) == {
        'boolean': {'saved': True, 'current': False}
    }


@pytest.mark.django_db
def test_verbose_mode_on_adding():
    tm = ModelTest()

    assert tm.get_dirty_fields(verbose=True) == {
        'boolean': {'saved': None, 'current': True},
        'characters': {'saved': None, 'current': u''}
    }


@pytest.mark.django_db
def test_refresh_from_db():
    tm = ModelTest.objects.create()
    alias = ModelTest.objects.get(pk=tm.pk)
    alias.boolean = False
    alias.save()

    tm.refresh_from_db()
    assert tm.get_dirty_fields() == {}


@pytest.mark.django_db
def test_refresh_from_db_particular_fields():
    tm = ModelTest.objects.create(characters="old value")
    tm.boolean = False
    tm.characters = "new value"
    assert tm.get_dirty_fields() == {"boolean": True, "characters": "old value"}

    tm.refresh_from_db(fields={"characters"})
    assert tm.boolean is False
    assert tm.characters == "old value"
    assert tm.get_dirty_fields() == {"boolean": True}


@pytest.mark.django_db
def test_refresh_from_db_no_fields():
    tm = ModelTest.objects.create(characters="old value")
    tm.boolean = False
    tm.characters = "new value"
    assert tm.get_dirty_fields() == {"boolean": True, "characters": "old value"}

    tm.refresh_from_db(fields=set())
    assert tm.boolean is False
    assert tm.characters == "new value"
    assert tm.get_dirty_fields() == {"boolean": True, "characters": "old value"}


@pytest.mark.django_db
def test_file_fields_content_file():
    tm = FileFieldModel()
    # field is dirty because model is unsaved
    assert tm.get_dirty_fields() == {"file1": FakeFieldFile("")}
    tm.save()
    assert tm.get_dirty_fields() == {}

    # set file makes field dirty
    tm.file1.save("test-file-1.txt", ContentFile(b"Test file content 1"), save=False)
    assert tm.get_dirty_fields() == {"file1": FakeFieldFile("")}
    tm.save()
    assert tm.get_dirty_fields() == {}

    # change file makes field dirty
    tm.file1.save("test-file-2.txt", ContentFile(b"Test file content 2"), save=False)
    assert tm.get_dirty_fields() == {"file1": FakeFieldFile("file1/test-file-1.txt")}
    tm.save()
    assert tm.get_dirty_fields() == {}


@pytest.mark.django_db
def test_file_fields_real_file():
    tm = FileFieldModel()
    # field is dirty because model is unsaved
    assert tm.get_dirty_fields() == {"file1": FakeFieldFile("")}
    tm.save()
    assert tm.get_dirty_fields() == {}

    # set file makes field dirty
    with open(join(dirname(__file__), "files", "foo.txt"), "rb") as f:
        tm.file1.save("test-file-3.txt", File(f), save=False)
    assert tm.get_dirty_fields() == {"file1": FakeFieldFile("")}
    tm.save()
    assert tm.get_dirty_fields() == {}

    # change file makes field dirty
    with open(join(dirname(__file__), "files", "bar.txt"), "rb") as f:
        tm.file1.save("test-file-4.txt", File(f), save=False)
    assert tm.get_dirty_fields() == {"file1": FakeFieldFile("file1/test-file-3.txt")}
    tm.save()
    assert tm.get_dirty_fields() == {}
