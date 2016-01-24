import pytest
import pytz
from datetime import datetime

from django.test.utils import override_settings

from .models import TestDatetimeModel


@override_settings(USE_TZ=True, TIME_ZONE='America/Chicago')
@pytest.mark.django_db
def test_datetime_fields_when_aware_db_and_naive_current_value():
    tm = TestDatetimeModel.objects.create(datetime_field=datetime(2000, 1, 1, tzinfo=pytz.utc))

    # initial state shouldn't be dirty
    assert not tm.is_dirty()

    # Adding a naive datetime
    tm.datetime_field = datetime(2016, 1, 1)

    # 'characters' is not tracked as it is deferred
    assert tm.get_dirty_fields() == {'datetime_field': datetime(2000, 1, 1, tzinfo=pytz.utc)}


@override_settings(USE_TZ=False)
@pytest.mark.django_db
def test_datetime_fields_when_naive_db_and_aware_current_value():

    tm = TestDatetimeModel.objects.create(datetime_field=datetime(2000, 1, 1))

    # initial state shouldn't be dirty
    assert not tm.is_dirty()

    # Adding a naive datetime
    tm.datetime_field = datetime(2016, 1, 1, tzinfo=pytz.utc)

    # 'characters' is not tracked as it is deferred
    assert tm.get_dirty_fields() == {'datetime_field': datetime(2000, 1, 1)}
