import pytest
import re

from django.db import connection
from django.db import IntegrityError
from django.test.utils import override_settings

from .models import (TestModel, TestModelWithForeignKey, TestModelWithNonEditableFields,
                     OrdinaryTestModel, OrdinaryTestModelWithForeignKey, TestModelWithSelfForeignKey,
                     TestExpressionModel)


@pytest.mark.django_db
def test_dirty_fields_ignores_the_editable_property_of_fields():
    # Non regression test case for bug:
    # https://github.com/smn/django-dirtyfields/issues/17
    tm = TestModelWithNonEditableFields.objects.create()

    # initial state shouldn't be dirty
    assert tm.get_dirty_fields() == {}

    # changing values should flag them as dirty
    tm.boolean = False
    tm.characters = 'testing'
    assert tm.get_dirty_fields() == {
        'boolean': True,
        'characters': ''
    }
    assert tm.get_dirty_fields(check_relationship=True) == {
        'boolean': True,
        'characters': ''
    }

    # resetting them to original values should unflag
    tm.boolean = True
    assert tm.get_dirty_fields() == {
        'characters': ''
    }
    assert tm.get_dirty_fields(check_relationship=True) == {
        'characters': ''
    }


@pytest.mark.django_db
def test_mandatory_foreign_key_field_not_initialized_is_not_raising_related_object_exception():
    # Non regression test case for bug:
    # https://github.com/smn/django-dirtyfields/issues/26
    with pytest.raises(IntegrityError):
        TestModelWithForeignKey.objects.create()


def _get_query_num(model_class):
    cnt = 0

    if hasattr(model_class._meta, 'model_name'):
        model_name = model_class._meta.model_name
    else:  # < 1.6
        model_name = model_class._meta.module_name

    pattern = re.compile(r'^.*SELECT.*FROM "tests_%s".*$' % model_name)

    for query in connection.queries:
        sql = query.get('sql')
        if pattern.match(sql):
            cnt += 1

    return cnt


@pytest.mark.django_db
@override_settings(DEBUG=True)  # The test runner sets DEBUG to False. Set to True to enable SQL logging.
def test_relationship_model_loading_issue():
    # Non regression test case for bug:
    # https://github.com/smn/django-dirtyfields/issues/34

    # Query tests with models that are not using django-dirtyfields
    tm1 = OrdinaryTestModel.objects.create()
    tm2 = OrdinaryTestModel.objects.create()
    OrdinaryTestModelWithForeignKey.objects.create(fkey=tm1)
    OrdinaryTestModelWithForeignKey.objects.create(fkey=tm2)

    for tmf in OrdinaryTestModelWithForeignKey.objects.all():
        tmf.pk

    assert _get_query_num(OrdinaryTestModelWithForeignKey) ==  1
    assert _get_query_num(OrdinaryTestModel) == 0  # should be 0 since we don't access the relationship for now.

    for tmf in OrdinaryTestModelWithForeignKey.objects.all():
        tmf.fkey  # access the relationship here

    assert _get_query_num(OrdinaryTestModelWithForeignKey) - 1 == 1
    assert _get_query_num(OrdinaryTestModel) == 2  # should be 2

    for tmf in OrdinaryTestModelWithForeignKey.objects.select_related('fkey').all():
        tmf.fkey  # access the relationship here

    assert _get_query_num(OrdinaryTestModelWithForeignKey) - 2 == 1
    assert _get_query_num(OrdinaryTestModel) - 2 == 0  # should be 0 since we use `select_related`

    # Query tests with models that are using django-dirtyfields
    tm1 = TestModel.objects.create()
    tm2 = TestModel.objects.create()
    TestModelWithForeignKey.objects.create(fkey=tm1)
    TestModelWithForeignKey.objects.create(fkey=tm2)

    for tmf in TestModelWithForeignKey.objects.all():
        tmf.pk  # we don't need the relationship here

    assert _get_query_num(TestModelWithForeignKey) == 1
    assert _get_query_num(TestModel) == 0  # should be 0, was 2 before bug fixing

    for tmf in TestModelWithForeignKey.objects.all():
        tmf.fkey  # access the relationship here

    assert _get_query_num(TestModelWithForeignKey) - 1 == 1
    assert _get_query_num(TestModel) == 2  # should be 0, but the relationship is loaded by DirtyFieldsMixin

    for tmf in TestModelWithForeignKey.objects.select_related('fkey').all():
        tmf.fkey  # access the relationship here

    assert _get_query_num(TestModelWithForeignKey) - 2 == 1
    assert _get_query_num(TestModel) - 2 == 0  # should be 0 since we use `selected_related` (was 2 before)


@pytest.mark.django_db
def test_relationship_option_for_foreign_key_to_self():
    # Non regression test case for bug:
    # https://github.com/smn/django-dirtyfields/issues/22
    tm = TestModelWithSelfForeignKey.objects.create()
    tm1 = TestModelWithSelfForeignKey.objects.create(fkey=tm)

    tm.fkey = tm1
    tm.save()

    # Trying to access an instance was triggering a "RuntimeError: maximum recursion depth exceeded"
    TestModelWithSelfForeignKey.objects.all()[0]


@pytest.mark.django_db
def test_expressions_not_taken_into_account_for_dirty_check():
    # Non regression test case for bug:
    # https://github.com/smn/django-dirtyfields/issues/39
    from django.db.models import F
    tm = TestExpressionModel.objects.create()
    tm.counter = F('counter') + 1

    # This save() was raising a ValidationError: [u"'F(counter) + Value(1)' value must be an integer."]
    # caused by a call to_python() on an expression node
    tm.save()
