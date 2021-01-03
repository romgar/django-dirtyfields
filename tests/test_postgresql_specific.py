import pytest

from tests.utils import is_postgresql_env_with_jsonb_field


@pytest.mark.skipif(not is_postgresql_env_with_jsonb_field(),
                    reason="requires postgresql >= 9.4.0 with jsonb field")
@pytest.mark.django_db
def test_dirty_jsonb_field():
    from tests.models import ModelWithJSONBFieldTest

    tm = ModelWithJSONBFieldTest.objects.create(jsonb_field={'data': [1, 2, 3]})

    data = tm.jsonb_field['data']
    data.append(4)

    assert tm.get_dirty_fields(verbose=True) == {
        'jsonb_field': {
            'current': {'data': [1, 2, 3, 4]},
            'saved': {'data': [1, 2, 3]}
        }
    }
