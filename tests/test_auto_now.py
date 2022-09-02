import pytest

from django.test.utils import override_settings

from .models import AutoNowDatetimeModel


@pytest.mark.django_db
@override_settings(DIRTYFIELDS_UPDATE_AUTO_NOW=True)
def test_auto_now_updated_on_save_dirty_fields():
    tm = AutoNowDatetimeModel.objects.create(test_string="test")

    previous_datetime = tm.datetime_field
    previous_date = tm.date_field

    # If the object has just been saved in the db, fields are not dirty
    assert not tm.is_dirty()

    # As soon as we change a field, it becomes dirty
    tm.test_string = "changed"
    assert tm.is_dirty()

    assert tm.get_dirty_fields() == {
        "test_string": "test",
        "datetime_field": previous_datetime,
        "date_field": previous_date,
    }
    tm.save_dirty_fields()
    tm.refresh_from_db()
    assert tm.datetime_field > previous_datetime
    assert tm.date_field == previous_date  # date most likely will not change during updates
