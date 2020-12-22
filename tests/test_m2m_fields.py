import pytest

from .models import ModelTest, Many2ManyModelTest, ModelWithCustomPKTest, M2MModelWithCustomPKOnM2MTest, \
    ModelWithoutM2MCheckTest, Many2ManyWithoutMany2ManyModeEnabledModelTest


@pytest.mark.django_db
def test_dirty_fields_on_m2m():
    tm = Many2ManyModelTest.objects.create()
    tm2 = ModelTest.objects.create()
    tm.m2m_field.add(tm2)

    assert tm._as_dict_m2m() == {'m2m_field': set([tm2.id])}

    # m2m check should be explicit: you have to give the values you want to compare with db state.
    # This first assertion means that m2m_field has one element of id tm2 in the database.
    assert tm.get_dirty_fields(check_m2m={'m2m_field': set([tm2.id])}) == {}

    # This second assertion means that I'm expecting a m2m_field that is related to an element with id 0
    # As it differs, we return the previous saved elements.
    assert tm.get_dirty_fields(check_m2m={'m2m_field': set([0])}) == {'m2m_field': set([tm2.id])}

    assert tm.get_dirty_fields(check_m2m={'m2m_field': set([0, tm2.id])}) == {'m2m_field': set([tm2.id])}


@pytest.mark.django_db
def test_dirty_fields_on_m2m_not_possible_if_not_enabled():
    tm = Many2ManyWithoutMany2ManyModeEnabledModelTest.objects.create()
    tm2 = ModelTest.objects.create()
    tm.m2m_field.add(tm2)

    with pytest.raises(ValueError):
        assert tm.get_dirty_fields(check_m2m={'m2m_field': set([tm2.id])}) == {}


@pytest.mark.django_db
def test_m2m_check_with_custom_primary_key():
    # test for bug: https://github.com/romgar/django-dirtyfields/issues/74

    tm = ModelWithCustomPKTest.objects.create(custom_primary_key='pk1')
    m2m_model = M2MModelWithCustomPKOnM2MTest.objects.create()

    # This line was triggering this error:
    # AttributeError: 'ModelWithCustomPKTest' object has no attribute 'id'
    m2m_model.m2m_field.add(tm)


@pytest.mark.django_db
def test_m2m_disabled_does_not_allow_to_check_m2m_fields():
    tm = ModelWithoutM2MCheckTest.objects.create()

    with pytest.raises(Exception):
        assert tm.get_dirty_fields(check_m2m={'dummy': True})
