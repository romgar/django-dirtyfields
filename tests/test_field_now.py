from copy import deepcopy
import pytest

from django.db.models.functions import Now

from .models import TestDatetimeModelStandard


@pytest.mark.django_db
def test_dirty_fields_field_now():
    tm = TestDatetimeModelStandard.objects.create()

    assert tm.get_dirty_fields() == {}

    tm.datetime_field = Now()

    assert tm.get_dirty_fields() == {'datetime_field': None}


@pytest.mark.django_db
def test_dirty_fields_field_now2():
    # we can't compare Now() values, so just test keys

    tm = TestDatetimeModelStandard.objects.create(datetime_field=Now())

    assert set(tm.get_dirty_fields().keys()) == {'datetime_field'}

    tm.datetime_field = Now()

    assert set(tm.get_dirty_fields().keys()) == {'datetime_field'}
