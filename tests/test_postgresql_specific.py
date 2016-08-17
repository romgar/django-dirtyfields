import pytest

from tests.utils import is_postgresql_env_with_json_field


@pytest.mark.skipif(not is_postgresql_env_with_json_field(),
                    reason="requires postgresql and Django 1.9+")
@pytest.mark.django_db
def test_dirty_json_field():
    from tests.models import TestModelWithJSONField

    tm = TestModelWithJSONField.objects.create(json_field={'data': 'dummy_data'})
    assert tm.get_dirty_fields() == {}

    tm.json_field = {'data': 'foo'}
    assert tm.get_dirty_fields() == {'json_field': {'data': 'dummy_data'}}
