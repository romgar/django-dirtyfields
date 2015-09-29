import pytest

from .models import TestModel, TestMixedFieldsModel
from tests.compat import skip_before_django_15
from .utils import assert_number_of_queries_on_regex


# We don't test it in django 1.5 because we are using 1.5+ 'update_fields' kwargs
# in our custom save_dirty_fields method
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
    assert not tm.is_dirty()
    assert TestModel.objects.get(pk=tm.pk).characters == 'new_character_2'


# We don't test it in django 1.5 because we are using 1.5+ 'update_fields' kwargs
# in our custom save_dirty_fields method
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
    assert not tmfm.is_dirty()
    assert TestMixedFieldsModel.objects.get(pk=tmfm.pk).fkey_id == tm1.id
