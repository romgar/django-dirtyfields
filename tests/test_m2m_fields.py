import pytest

from django.db import IntegrityError
from django.test.utils import override_settings

from .models import (TestModel, TestModelWithForeignKey,
                     OrdinaryTestModel, OrdinaryTestModelWithForeignKey, TestModelWithSelfForeignKey,
                     TestExpressionModel, TestM2MModel)
from .utils import assert_select_number_queries_on_model


@pytest.mark.django_db
def test_dirty_fields_on_m2m():
    # Non regression test case for bug:
    # https://github.com/romgar/django-dirtyfields/issues/17
    tm = TestM2MModel.objects.create()

    # initial state shouldn't be dirty
    tm2 = TestModel.objects.create()
    tm.m2m_field.add(tm2)

    assert tm._as_dict_m2m() == {'m2m_field': set([tm2.id])}

    assert tm.get_dirty_fields(check_m2m={'m2m_field': set([tm2.id])}) == {'m2m_field': set([])}
