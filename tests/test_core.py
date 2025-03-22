from decimal import Decimal
from os.path import dirname, join

import pytest
import django
from django.core.files.base import ContentFile, File
from django.db import DatabaseError, transaction

import dirtyfields
from .models import (ModelTest, ModelWithForeignKeyTest,
                     ModelWithOneToOneFieldTest,
                     SubclassModelTest, ModelWithDecimalFieldTest,
                     FileFieldModel, OrdinaryModelTest, OrdinaryWithDirtyFieldsProxy)


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
def test_refresh_from_db_position_args():
    tm = ModelTest.objects.create(characters="old value")
    tm.boolean = False
    tm.characters = "new value"
    assert tm.get_dirty_fields() == {"boolean": True, "characters": "old value"}

    tm.refresh_from_db("default", {"boolean", "characters"})
    assert tm.boolean is True
    assert tm.characters == "old value"
    assert tm.get_dirty_fields() == {}


@pytest.mark.skipif(django.VERSION < (5, 1), reason="requires django 5.1 or higher")
@pytest.mark.django_db
def test_refresh_from_db_with_from_queryset():
    """Tests passthrough of `from_queryset` field in refresh_from_db
    this field was introduced in django 5.1. more details in this PR:
    https://github.com/romgar/django-dirtyfields/pull/235
    """
    tm = ModelTest.objects.create(characters="old value")
    tm.boolean = False
    tm.characters = "new value"
    assert tm.get_dirty_fields() == {"boolean": True, "characters": "old value"}

    tm.refresh_from_db(fields={"characters"}, from_queryset=ModelTest.objects.all())
    assert tm.boolean is False
    assert tm.characters == "old value"
    assert tm.get_dirty_fields() == {"boolean": True}


@pytest.mark.skipif(django.VERSION < (5, 1), reason="requires django 5.1 or higher")
@pytest.mark.django_db
def test_refresh_from_db_position_args_with_queryset():
    tm = ModelTest.objects.create(characters="old value")
    tm.boolean = False
    tm.characters = "new value"
    assert tm.get_dirty_fields() == {"boolean": True, "characters": "old value"}

    tm.refresh_from_db("default", {"characters"}, ModelTest.objects.all())
    assert tm.boolean is False
    assert tm.characters == "old value"
    assert tm.get_dirty_fields() == {"boolean": True}


@pytest.mark.django_db
def test_file_fields_content_file():
    tm = FileFieldModel()
    # field is dirty because model is unsaved
    assert tm.get_dirty_fields(verbose=True) == {
        "file1": {"current": "", "saved": None},
    }
    tm.save()
    assert tm.get_dirty_fields() == {}

    # set file makes field dirty
    tm.file1.save("test-file-1.txt", ContentFile(b"Test file content"), save=False)
    assert tm.get_dirty_fields(verbose=True) == {
        "file1": {"current": "file1/test-file-1.txt", "saved": ""},
    }
    tm.save()
    assert tm.get_dirty_fields() == {}

    # change field to new file makes field dirty
    tm.file1.save("test-file-2.txt", ContentFile(b"Test file content"), save=False)
    assert tm.get_dirty_fields(verbose=True) == {
        "file1": {"current": "file1/test-file-2.txt", "saved": "file1/test-file-1.txt"},
    }
    tm.save()
    assert tm.get_dirty_fields() == {}

    # change field to new file and new content makes field dirty
    tm.file1.save("test-file-3.txt", ContentFile(b"Test file content 3"), save=False)
    assert tm.get_dirty_fields(verbose=True) == {
        "file1": {"current": "file1/test-file-3.txt", "saved": "file1/test-file-2.txt"},
    }
    tm.save()
    assert tm.get_dirty_fields() == {}

    # change file content without changing file name does not make field dirty
    tm.file1.open("w")
    tm.file1.write("Test file content edited")
    tm.file1.close()
    assert tm.file1.name == "file1/test-file-3.txt"
    assert tm.get_dirty_fields() == {}
    tm.file1.open("r")
    assert tm.file1.read() == "Test file content edited"
    tm.file1.close()


@pytest.mark.django_db
def test_file_fields_real_file():
    tm = FileFieldModel()
    # field is dirty because model is unsaved
    assert tm.get_dirty_fields(verbose=True) == {
        "file1": {"current": "", "saved": None},
    }
    tm.save()
    assert tm.get_dirty_fields() == {}

    # set file makes field dirty
    with open(join(dirname(__file__), "files", "foo.txt"), "rb") as f:
        tm.file1.save("test-file-4.txt", File(f), save=False)
    assert tm.get_dirty_fields(verbose=True) == {
        "file1": {"current": "file1/test-file-4.txt", "saved": ""},
    }
    tm.save()
    assert tm.get_dirty_fields() == {}

    # change field to new file makes field dirty
    with open(join(dirname(__file__), "files", "bar.txt"), "rb") as f:
        tm.file1.save("test-file-5.txt", File(f), save=False)
    assert tm.get_dirty_fields(verbose=True) == {
        "file1": {"current": "file1/test-file-5.txt", "saved": "file1/test-file-4.txt"},
    }
    tm.save()
    assert tm.get_dirty_fields() == {}

    # change field to new file with same content makes field dirty
    with open(join(dirname(__file__), "files", "bar.txt"), "rb") as f:
        tm.file1.save("test-file-6.txt", File(f), save=False)
    assert tm.get_dirty_fields(verbose=True) == {
        "file1": {"current": "file1/test-file-6.txt", "saved": "file1/test-file-5.txt"},
    }
    tm.save()
    assert tm.get_dirty_fields() == {}

    # change file content without changing file name does not make field dirty
    tm.file1.open("w")
    tm.file1.write("Test file content edited")
    tm.file1.close()
    assert tm.file1.name == "file1/test-file-6.txt"
    assert tm.get_dirty_fields() == {}
    tm.file1.open("r")
    assert tm.file1.read() == "Test file content edited"
    tm.file1.close()


@pytest.mark.django_db
def test_transaction_behavior():
    """This test is to document the behavior in transactions"""
    # first create a model
    tm = ModelTest.objects.create(boolean=True, characters="first")
    assert not tm.is_dirty()

    # make an edit in-memory, model becomes dirty
    tm.characters = "second"
    assert tm.get_dirty_fields() == {"characters": "first"}

    # attempt to save the model in a transaction
    try:
        with transaction.atomic():
            tm.save()
            # no longer dirty because save() has been called, BUT we are still in a transaction ...
            assert not tm.is_dirty()
            assert tm.get_dirty_fields() == {}
            # force a transaction rollback
            raise DatabaseError("pretend something went wrong")
    except DatabaseError:
        pass

    # Here is the problem:
    # value in DB is still "first" but model does not think its dirty.
    assert tm.characters == "second"
    assert not tm.is_dirty()  # <---- In an ideal world this would be dirty
    assert tm.get_dirty_fields() == {}

    # here is a workaround, after failed transaction call refresh_from_db()
    tm.refresh_from_db()
    assert tm.characters == "first"
    assert tm.get_dirty_fields() == {}
    # test can become dirty again
    tm.characters = "third"
    assert tm.is_dirty()
    assert tm.get_dirty_fields() == {"characters": "first"}


@pytest.mark.django_db
def test_proxy_model_behavior():
    tm = OrdinaryModelTest.objects.create()

    dirty_tm = OrdinaryWithDirtyFieldsProxy.objects.get(id=tm.id)
    assert not dirty_tm.is_dirty()
    assert dirty_tm.get_dirty_fields() == {}

    dirty_tm.boolean = False
    dirty_tm.characters = "hello"
    assert dirty_tm.is_dirty()
    assert dirty_tm.get_dirty_fields() == {"characters": "", "boolean": True}

    dirty_tm.save()
    assert not dirty_tm.is_dirty()
    assert dirty_tm.get_dirty_fields() == {}

    tm.refresh_from_db()
    assert tm.boolean is False
    assert tm.characters == "hello"
