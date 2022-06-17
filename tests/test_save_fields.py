import pytest

from django.db.models import F

from .models import (
    ExpressionModelTest,
    MixedFieldsModelTest,
    ModelTest,
    ModelWithForeignKeyTest,
)
from .utils import assert_number_of_queries_on_regex


@pytest.mark.django_db
def test_save_dirty_simple_field():
    tm = ModelTest.objects.create()

    tm.characters = 'new_character'

    with assert_number_of_queries_on_regex(r'.*characters.*', 1):
        with assert_number_of_queries_on_regex(r'.*boolean.*', 1):
            tm.save()

    tm.characters = 'new_character_2'

    # Naive checking on fields involved in Django query
    # boolean unchanged field is not updated on Django update query: GOOD !
    with assert_number_of_queries_on_regex(r'.*characters.*', 1):
        with assert_number_of_queries_on_regex(r'.*boolean.*', 0):
            tm.save_dirty_fields()

    # We also check that the value has been correctly updated by our custom function
    assert tm.get_dirty_fields() == {}
    assert ModelTest.objects.get(pk=tm.pk).characters == 'new_character_2'


@pytest.mark.django_db
def test_save_dirty_related_field():
    tm1 = ModelTest.objects.create()
    tm2 = ModelTest.objects.create()
    tmfm = MixedFieldsModelTest.objects.create(fkey=tm1)

    tmfm.fkey = tm2

    with assert_number_of_queries_on_regex(r'.*fkey_id.*', 1):
        with assert_number_of_queries_on_regex(r'.*characters.*', 1):
            tmfm.save()

    tmfm.fkey = tm1

    # Naive checking on fields involved in Django query
    # characters unchanged field is not updated on Django update query: GOOD !
    with assert_number_of_queries_on_regex(r'.*fkey_id.*', 1):
        with assert_number_of_queries_on_regex(r'.*characters.*', 0):
            tmfm.save_dirty_fields()

    # We also check that the value has been correctly updated by our custom function
    assert tmfm.get_dirty_fields() == {}
    assert MixedFieldsModelTest.objects.get(pk=tmfm.pk).fkey_id == tm1.id


@pytest.mark.django_db
def test_save_dirty_full_save_on_adding():
    tm = ModelTest()
    tm.save_dirty_fields()
    assert tm.pk
    assert tm.get_dirty_fields() == {}


@pytest.mark.django_db
def test_save_only_specific_fields_should_let_other_fields_dirty():
    tm = ModelTest.objects.create(boolean=True, characters='dummy')

    tm.boolean = False
    tm.characters = 'new_dummy'

    tm.save(update_fields=['boolean'])

    # 'characters' field should still be dirty, update_fields was only saving the 'boolean' field in the db
    assert tm.get_dirty_fields() == {'characters': 'dummy'}


@pytest.mark.django_db
def test_save_empty_update_fields_wont_reset_dirty_state():
    tm = ModelTest.objects.create(boolean=True, characters='dummy')

    tm.boolean = False
    tm.characters = 'new_dummy'
    assert tm.get_dirty_fields() == {"boolean": True, 'characters': 'dummy'}

    # Django docs say "An empty update_fields iterable will skip the save",
    # so this should not change the dirty state.
    tm.save(update_fields=[])

    assert tm.boolean is False
    assert tm.characters == "new_dummy"
    assert tm.get_dirty_fields() == {"boolean": True, 'characters': 'dummy'}


@pytest.mark.django_db
def test_handle_foreignkeys_id_field_in_update_fields():
    tm1 = ModelTest.objects.create(boolean=True, characters='dummy')
    tm2 = ModelTest.objects.create(boolean=True, characters='dummy')
    tmwfk = ModelWithForeignKeyTest.objects.create(fkey=tm1)

    tmwfk.fkey = tm2
    assert tmwfk.get_dirty_fields(check_relationship=True) == {'fkey': tm1.pk}

    tmwfk.save(update_fields=['fkey_id'])
    assert tmwfk.get_dirty_fields(check_relationship=True) == {}


@pytest.mark.django_db
def test_correctly_handle_foreignkeys_id_field_in_update_fields():
    tm1 = ModelTest.objects.create(boolean=True, characters='dummy')
    tm2 = ModelTest.objects.create(boolean=True, characters='dummy')
    tmwfk = ModelWithForeignKeyTest.objects.create(fkey=tm1)

    tmwfk.fkey_id = tm2.pk
    assert tmwfk.get_dirty_fields(check_relationship=True) == {'fkey': tm1.pk}

    tmwfk.save(update_fields=['fkey'])
    assert tmwfk.get_dirty_fields(check_relationship=True) == {}


@pytest.mark.django_db
def test_save_deferred_field_with_update_fields():
    ModelTest.objects.create()

    tm = ModelTest.objects.defer('boolean').first()
    tm.boolean = False
    # Test that providing a deferred field to the update_fields
    # save parameter doesn't raise a KeyError anymore.
    tm.save(update_fields=['boolean'])


@pytest.mark.django_db
def test_deferred_field_was_not_dirty():
    ModelTest.objects.create()
    tm = ModelTest.objects.defer('boolean').first()
    tm.boolean = False
    assert tm.get_dirty_fields() == {}


@pytest.mark.django_db
def test_save_deferred_field_with_update_fields_behaviour():
    """ Behaviour of deferred fields has changed in Django 1.10.
    Once explicitly updated (using the save update_fields parameter),
    a field cannot be considered deferred anymore.
    """

    ModelTest.objects.create()
    tm = ModelTest.objects.defer('boolean').first()
    tm.save(update_fields=['boolean'])
    tm.boolean = False
    assert tm.get_dirty_fields() == {'boolean': True}


@pytest.mark.django_db
def test_get_dirty_fields_when_saving_with_f_objects():
    """
    This documents how get_dirty_fields() behaves when updating model fields
    with F objects.
    """

    tm = ExpressionModelTest.objects.create(counter=0)
    assert tm.counter == 0
    assert tm.get_dirty_fields() == {}

    tm.counter = F("counter") + 1
    # tm.counter field is not considered dirty because it doesn't have a simple
    # value in memory we can compare to the original value.
    # i.e. we don't know what value it will be in the database after the F
    # object is translated into SQL.
    assert tm.get_dirty_fields() == {}

    tm.save()
    # tm.counter is still an F object after save() - we don't know the new
    # value in the database.
    assert tm.get_dirty_fields() == {}

    tm.counter = 10
    # even though we have now assigned a literal value to tm.counter, we don't
    # know the value in the database, so it is not considered dirty.
    assert tm.get_dirty_fields() == {}

    tm.save()
    assert tm.get_dirty_fields() == {}

    tm.refresh_from_db()
    # if we call refresh_from_db(), we load the database value,
    # so we can assign a value and make the field dirty again.
    tm.counter = 20
    assert tm.get_dirty_fields() == {"counter": 10}


@pytest.mark.django_db
def test_get_dirty_fields_when_saving_with_f_objects_update_fields_specified():
    """
    Same as above but with update_fields specified when saving/refreshing
    """

    tm = ExpressionModelTest.objects.create(counter=0)
    assert tm.counter == 0
    assert tm.get_dirty_fields() == {}

    tm.counter = F("counter") + 1
    assert tm.get_dirty_fields() == {}

    tm.save(update_fields={"counter"})
    assert tm.get_dirty_fields() == {}

    tm.counter = 10
    assert tm.get_dirty_fields() == {}

    tm.save(update_fields={"counter"})
    assert tm.get_dirty_fields() == {}

    tm.refresh_from_db(fields={"counter"})
    tm.counter = 20
    assert tm.get_dirty_fields() == {"counter": 10}
