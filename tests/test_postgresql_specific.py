import pytest

from tests.models import ModelWithJSONBFieldTest


@pytest.mark.django_db
def test_dirty_jsonb_field():
    tm = ModelWithJSONBFieldTest.objects.create(jsonb_field={'data': [1, 2, 3]})

    data = tm.jsonb_field['data']
    data.append(4)

    assert tm.get_dirty_fields(verbose=True) == {
        'jsonb_field': {
            'current': {'data': [1, 2, 3, 4]},
            'saved': {'data': [1, 2, 3]}
        }
    }
