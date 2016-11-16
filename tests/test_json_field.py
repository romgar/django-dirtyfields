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


@unittest.skipIf(not JSON_FIELD_AVAILABLE, 'django jsonfield library required')
@pytest.mark.django_db
def test_json_field():
    tm = JSONFieldModel.objects.create(json_field={'data': [1, 2, 3]})

    data = tm.json_field['data']
    data.append(4)

    assert tm.get_dirty_fields() == {
        'json_field': {'data': [1, 2, 3]}
    }
