import pytest

from tests.models import ModelWithJSONFieldThirdPartyTest


@pytest.mark.django_db
def test_json_field_third_party():
    tm = ModelWithJSONFieldThirdPartyTest.objects.create(json_field_third_party={'data': [1, 2, 3]})

    data = tm.json_field_third_party['data']
    data.append(4)

    assert tm.get_dirty_fields() == {
        'json_field_third_party': {'data': [1, 2, 3]}
    }
