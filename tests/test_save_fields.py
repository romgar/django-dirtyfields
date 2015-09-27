import pytest

from .models import TestModel
from tests.compat import skip_before_django_15
from .utils import assert_number_of_queries_on_regex


@skip_before_django_15
@pytest.mark.django_db
def test_save_dirty_simple_field():
    tm = TestModel.objects.create()

    tm.characters = 'new_character'

    with assert_number_of_queries_on_regex(r'.*characters.*', 1):
        with assert_number_of_queries_on_regex(r'.*boolean.*', 1):
            tm.save()

    assert TestModel.objects.get(pk=tm.pk).characters == 'new_character'

    tm.characters = 'new_character_2'

    with assert_number_of_queries_on_regex(r'.*characters.*', 1):
        with assert_number_of_queries_on_regex(r'.*boolean.*', 0):
            tm.save_dirty_fields()

    assert TestModel.objects.get(pk=tm.pk).characters == 'new_character_2'
