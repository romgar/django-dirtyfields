from decimal import Decimal
import pytest

from .models import TestAutoNowDatetimeModel


@pytest.mark.django_db
def test_auto_now_updated_on_save_dirty_fields():
    tm = TestAutoNowDatetimeModel.objects.create(test_string="test")

    previous_datetime = tm.datetime_field
    previous_date = tm.date_field

    # If the object has just been saved in the db, fields are not dirty
    assert not tm.is_dirty()

    # As soon as we change a field, it becomes dirty
    tm.test_string = "changed"
    assert tm.is_dirty()

    assert tm.get_dirty_fields(include_auto_now=True) == {
        "test_string": "test",
        "datetime_field": previous_datetime,
        "date_field": previous_date,
    }
    tm.save_dirty_fields(include_auto_now=True)
    tm.refresh_from_db()
    assert tm.datetime_field > previous_datetime
    assert tm.date_field == previous_date  # date most likely will not change during updates
