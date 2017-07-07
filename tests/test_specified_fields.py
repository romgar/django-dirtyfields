import pytest

from .models import TestModel, TestModelWithSpecifiedFields, TestModelWithM2MAndSpecifiedFields


@pytest.mark.django_db
def test_dirty_fields_on_model_with_specified_fields():
    tm = TestModelWithSpecifiedFields.objects.create()

    tm.boolean1 = False
    tm.boolean2 = False

    # boolean1 is tracked, boolean2 isn`t tracked
    assert tm.get_dirty_fields() == {'boolean1': True}


@pytest.mark.django_db
def test_dirty_fields_on_model_with_m2m_and_specified_fields():
    tm = TestModelWithM2MAndSpecifiedFields.objects.create()
    tm2 = TestModel.objects.create()

    tm.m2m1.add(tm2)
    tm.m2m2.add(tm2)

    # m2m1 is tracked, m2m2 isn`t tracked
    assert tm.get_dirty_fields(check_m2m={'m2m1': set([])}) == {'m2m1': set([tm2.id])}
    assert tm.get_dirty_fields(check_m2m={'m2m2': set([])}) == {}

