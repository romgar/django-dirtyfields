import pytest

from .models import (
    ModelTest,
    ModelWithSpecifiedFieldsTest,
    ModelWithM2MAndSpecifiedFieldsTest,
    ModelWithSpecifiedFieldsAndForeignKeyTest,
    ModelWithSpecifiedFieldsAndForeignKeyTest2
)


@pytest.mark.django_db
def test_dirty_fields_on_model_with_specified_fields():
    tm = ModelWithSpecifiedFieldsTest.objects.create()

    tm.boolean1 = False
    tm.boolean2 = False

    # boolean1 is tracked, boolean2 isn`t tracked
    assert tm.get_dirty_fields() == {'boolean1': True}


@pytest.mark.django_db
def test_dirty_fields_on_model_with_m2m_and_specified_fields():
    tm = ModelWithM2MAndSpecifiedFieldsTest.objects.create()
    tm2 = ModelTest.objects.create()

    tm.m2m1.add(tm2)
    tm.m2m2.add(tm2)

    # m2m1 is tracked, m2m2 isn`t tracked
    assert tm.get_dirty_fields(check_m2m={'m2m1': set([])}) == {'m2m1': set([tm2.id])}
    assert tm.get_dirty_fields(check_m2m={'m2m2': set([])}) == {}


@pytest.mark.django_db
def test_dirty_fields_on_model_with_specified_fields_can_save_when_non_tracked_field_is_modified():
    tm = ModelWithSpecifiedFieldsTest.objects.create()

    tm.boolean1 = False
    tm.boolean2 = False

    tm.save(update_fields=["boolean2"])

    assert "boolean1" in tm._original_state
    assert "boolean2" not in tm._original_state


@pytest.mark.django_db
def test_dirty_fields_on_model_with_specified_fields_can_save_when_non_tracked_fk_field_is_modified():
    tm = ModelWithSpecifiedFieldsAndForeignKeyTest.objects.create()
    fk = ModelTest.objects.create()
    tm.fk_field = fk
    tm.boolean1 = False
    tm.boolean2 = False

    tm.save(update_fields=["fk_field"])
    assert "fk_field" in tm._original_state

    tm.boolean2 = True
    tm.save()
    assert "fk_field" in tm._original_state
    assert "boolean2" not in tm._original_state


@pytest.mark.django_db
def test_dirty_fields_on_model_with_specified_fields_can_save_when_non_tracked_fk_field_is_modified_2():
    tm = ModelWithSpecifiedFieldsAndForeignKeyTest2.objects.create()
    fk = ModelTest.objects.create()
    tm.fk_field = fk
    tm.boolean1 = False
    tm.boolean2 = False

    tm.save(update_fields=["fk_field"])
    assert "fk_field" in tm._original_state

    tm.boolean2 = True
    tm.save()
    assert "fk_field" in tm._original_state
    assert "boolean2" not in tm._original_state
