from datetime import datetime, timedelta, timezone

import pytest
from django.test.utils import override_settings
from django.utils import timezone as django_timezone

from .models import DatetimeModelTest, CurrentDatetimeModelTest


@override_settings(USE_TZ=True)
@pytest.mark.django_db
def test_datetime_fields_when_aware_db_and_naive_current_value():
    tm = DatetimeModelTest.objects.create(datetime_field=datetime(2000, 1, 1, tzinfo=timezone.utc))

    # Adding a naive datetime
    tm.datetime_field = datetime(2016, 1, 1)

    with pytest.warns(
        RuntimeWarning,
        match=(
            r"DateTimeField received a naive datetime \(2016-01-01 00:00:00\) "
            r"while time zone support is active\."
        ),
    ):
        assert tm.get_dirty_fields() == {'datetime_field': datetime(2000, 1, 1, tzinfo=timezone.utc)}


@override_settings(USE_TZ=False)
@pytest.mark.django_db
def test_datetime_fields_when_naive_db_and_aware_current_value():
    tm = DatetimeModelTest.objects.create(datetime_field=datetime(2000, 1, 1))

    # Adding an aware datetime
    tm.datetime_field = datetime(2016, 1, 1, tzinfo=timezone.utc)

    with pytest.warns(
        RuntimeWarning,
        match=(
            r"Time zone support is not active \(settings\.USE_TZ=False\), "
            r"and you pass a time zone aware value "
            r"\(2016-01-01 00:00:00\+00:00\) "
            r"Converting database value before comparison\."
        ),
    ):
        assert tm.get_dirty_fields() == {'datetime_field': datetime(2000, 1, 1)}


@override_settings(USE_TZ=True)
@pytest.mark.django_db
def test_datetime_fields_when_aware_db_and_aware_current_value():
    aware_dt = django_timezone.now()
    tm = DatetimeModelTest.objects.create(datetime_field=aware_dt)

    tm.datetime_field = django_timezone.now()

    assert tm.get_dirty_fields() == {'datetime_field': aware_dt}


@override_settings(USE_TZ=False)
@pytest.mark.django_db
def test_datetime_fields_when_naive_db_and_naive_current_value():
    naive_dt = datetime.now()
    tm = DatetimeModelTest.objects.create(datetime_field=naive_dt)

    tm.datetime_field = datetime.now()

    assert tm.get_dirty_fields() == {'datetime_field': naive_dt}


@override_settings(USE_TZ=True, TIME_ZONE='America/Chicago')
@pytest.mark.django_db
def test_datetime_fields_with_current_timezone_conversion():
    tm = CurrentDatetimeModelTest.objects.create(datetime_field=datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc))

    # Adding a naive datetime, that will be converted to local timezone.
    tm.datetime_field = datetime(2000, 1, 1, 6, 0, 0)

    # Chicago is UTC-6h, this field shouldn't be dirty, as we will automatically set this naive datetime
    # with current timezone and then convert it to utc to compare it with database one.
    with pytest.warns(
        RuntimeWarning,
        match=(
            r"DateTimeField received a naive datetime "
            r"\(2000-01-01 06:00:00\) while time zone support is active\."
        ),
    ):
        assert tm.get_dirty_fields() == {}


@override_settings(USE_TZ=False, TIME_ZONE='America/Chicago')
@pytest.mark.django_db
def test_datetime_fields_with_current_timezone_conversion_without_timezone_support():
    tm = CurrentDatetimeModelTest.objects.create(datetime_field=datetime(2000, 1, 1, 12, 0, 0))

    # Adding an aware datetime, Chicago is UTC-6h
    chicago_timezone = timezone(timedelta(hours=-6))
    tm.datetime_field = datetime(2000, 1, 1, 6, 0, 0, tzinfo=chicago_timezone)

    # If the database is naive, then we consider that it is defined as in UTC.
    with pytest.warns(
        RuntimeWarning,
        match=(
            r"Time zone support is not active \(settings\.USE_TZ=False\), "
            r"and you pass a time zone aware value "
            r"\(2000-01-01 06:00:00-06:00\) "
            r"Converting database value before comparison\."
        ),
    ):
        assert tm.get_dirty_fields() == {}
