import unittest
import pytest
from django.db import models
from dirtyfields import DirtyFieldsMixin

JSON_FIELD_AVAILABLE = False
try:
    from jsonfield import JSONField
    JSON_FIELD_AVAILABLE = True
except ImportError:
    pass


if JSON_FIELD_AVAILABLE:
    class JSONFieldModel(DirtyFieldsMixin, models.Model):
        json_field = JSONField()


def skip_unless_jsonfield_library(test):
    if not JSON_FIELD_AVAILABLE:
        return unittest.skip('django jsonfield library required')(test)
    return test


@skip_unless_jsonfield_library
@pytest.mark.django_db
def test_json_field():
    tm = JSONFieldModel.objects.create(json_field={'data': 'dummy_data'})

    # initial state shouldn't be dirty
    is_dirty = tm.is_dirty()
    assert is_dirty is False

    tm.json_field['data'] = 'dummy_data_modified'

    assert tm.get_dirty_fields() == {
        'json_field': {'data': 'dummy_data'}
    }
