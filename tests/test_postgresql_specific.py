import pytest

from tests.utils import is_postgresql_env_with_json_field


@pytest.mark.skipif(not is_postgresql_env_with_json_field(),
                    reason="requires postgresql and Django 1.9+")
@pytest.mark.django_db
def test_dirty_json_field():
    from tests.models import TestModelWithJSONField

    tm = TestModelWithJSONField.objects.create(json_field={'data': [1, 2, 3]})

    data = tm.json_field['data']
    data.append(4)

    assert tm.get_dirty_fields(verbose=True) == {
        'json_field': {
            'current': {'data': [1, 2, 3, 4]},
            'saved': {'data': [1, 2, 3]}
        }
    }
