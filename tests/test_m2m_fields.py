import pytest

from .models import TestModel, TestM2MModel, TestModelWithCustomPK, TestM2MModelWithCustomPKOnM2M, \
    TestModelWithoutM2MCheck, TestM2MModelWithoutM2MModeEnabled


@pytest.mark.django_db
def test_dirty_fields_on_m2m(django_assert_num_queries):
    tm = TestM2MModel.objects.create()
    tm2 = TestModel.objects.create()
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
    tm = TestM2MModelWithoutM2MModeEnabled.objects.create()
    tm2 = TestModel.objects.create()
    tm.m2m_field.add(tm2)

    with pytest.raises(ValueError):
        assert tm.get_dirty_fields(check_m2m={'m2m_field': set([tm2.id])}) == {}


@pytest.mark.django_db
def test_m2m_check_with_custom_primary_key():
    # test for bug: https://github.com/romgar/django-dirtyfields/issues/74

    tm = TestModelWithCustomPK.objects.create(custom_primary_key='pk1')
    m2m_model = TestM2MModelWithCustomPKOnM2M.objects.create()

    # This line was triggering this error:
    # AttributeError: 'TestModelWithCustomPK' object has no attribute 'id'
    m2m_model.m2m_field.add(tm)


@pytest.mark.django_db
def test_m2m_disabled_does_not_allow_to_check_m2m_fields():
    tm = TestModelWithoutM2MCheck.objects.create()

    with pytest.raises(Exception):
        assert tm.get_dirty_fields(check_m2m={'dummy': True})


@pytest.mark.django_db
def test_dirty_fields_on_m2m_and_assert_num_queries(django_assert_num_queries):
    with django_assert_num_queries(2):
        tm = TestM2MModel.objects.create()
        tm2 = TestModel.objects.create()
    with django_assert_num_queries(4):
        tm.m2m_field.add(tm2)

    with django_assert_num_queries(1):
        tm3 = TestM2MModel.objects.get(id=tm.id)

    assert tm3.get_dirty_fields(check_m2m={'m2m_field': set([tm2.id])}) == {}
    assert tm.get_dirty_fields(check_m2m={'m2m_field': set([0])}) == {'m2m_field': set([tm2.id])}
    assert tm.get_dirty_fields(check_m2m={'m2m_field': set([0, tm2.id])}) == {'m2m_field': set([tm2.id])}