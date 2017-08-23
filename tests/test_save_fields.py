import unittest

import django
import pytest

from .models import TestModel, TestMixedFieldsModel, TestModelWithForeignKey
from .utils import assert_number_of_queries_on_regex


@pytest.mark.django_db
def test_save_dirty_simple_field():
    tm = TestModel.objects.create()

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
    assert TestModel.objects.get(pk=tm.pk).characters == 'new_character_2'


@pytest.mark.django_db
def test_save_dirty_related_field():
    tm1 = TestModel.objects.create()
    tm2 = TestModel.objects.create()
    tmfm = TestMixedFieldsModel.objects.create(fkey=tm1)

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
    assert TestMixedFieldsModel.objects.get(pk=tmfm.pk).fkey_id == tm1.id


@pytest.mark.django_db
def test_save_only_specific_fields_should_let_other_fields_dirty():
    tm = TestModel.objects.create(boolean=True, characters='dummy')

    tm.boolean = False
    tm.characters = 'new_dummy'

    tm.save(update_fields=['boolean'])

    # 'characters' field should still be dirty, update_fields was only saving the 'boolean' field in the db
    assert tm.get_dirty_fields() == {'characters': 'dummy'}


@pytest.mark.django_db
def test_handle_foreignkeys_id_field_in_update_fields():
    tm1 = TestModel.objects.create(boolean=True, characters='dummy')
    tm2 = TestModel.objects.create(boolean=True, characters='dummy')
    tmwfk = TestModelWithForeignKey.objects.create(fkey=tm1)

    tmwfk.fkey = tm2
    assert tmwfk.get_dirty_fields(check_relationship=True) == {'fkey': tm1.pk}

    tmwfk.save(update_fields=['fkey_id'])
    assert tmwfk.get_dirty_fields(check_relationship=True) == {}


@pytest.mark.django_db
def test_correctly_handle_foreignkeys_id_field_in_update_fields():
    tm1 = TestModel.objects.create(boolean=True, characters='dummy')
    tm2 = TestModel.objects.create(boolean=True, characters='dummy')
    tmwfk = TestModelWithForeignKey.objects.create(fkey=tm1)

    tmwfk.fkey_id = tm2.pk
    assert tmwfk.get_dirty_fields(check_relationship=True) == {'fkey': tm1.pk}

    tmwfk.save(update_fields=['fkey'])
    assert tmwfk.get_dirty_fields(check_relationship=True) == {}


@pytest.mark.django_db
def test_save_deferred_field_with_update_fields():
    TestModel.objects.create()

    tm = TestModel.objects.defer('boolean').first()
    tm.boolean = False
    # Test that providing a deferred field to the update_fields
    # save parameter doesn't raise a KeyError anymore.
    tm.save(update_fields=['boolean'])
