import pytest

from .models import TestModelWithSpecifiedFields



@pytest.mark.django_db
def test_fields_to_check():
    tm = TestModelWithSpecifiedFields.objects.create()

    tm.field_to_check = False
    tm.other_field = False

    # field_to_check is tracked, other_field isn`t tracked
    assert tm.get_dirty_fields() == {'field_to_check': True}

