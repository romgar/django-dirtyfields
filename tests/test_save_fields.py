import pytest
from .models import TestModel
from .utils import assert_number_queries


@pytest.mark.django_db
def test_save_specific_field():
    tm = TestModel.objects.create()

    tm.characters = 'new_character'
    tm.save()

    tm.characters = 'new_character_2'
    tm.save_dirty_fields()
