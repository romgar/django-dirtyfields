from decimal import Decimal
import re
import unittest
from django.db import connection
from django.db import IntegrityError
from django.test import TestCase
from django.test.utils import override_settings
from .models import (TestModel, TestModelWithForeignKey, TestModelWithNonEditableFields, TestModelWithOneToOneField,
                     OrdinaryTestModel, OrdinaryTestModelWithForeignKey, TestModelWithSelfForeignKey,
                     SubclassModel, TestModelWithDecimalField)



def skip_unless_jsonfield_library(test):
    try:
        from jsonfield import JSONField
    except ImportError:
        return unittest.skip('django jsonfield library required')(test)
    return test


class DirtyFieldsMixinTestCase(TestCase):

    def test_dirty_fields(self):
        tm = TestModel()
        # initial state shouldn't be dirty
        self.assertEqual(tm.get_dirty_fields(), {})

        # changing values should flag them as dirty
        tm.boolean = False
        tm.characters = 'testing'
        self.assertEqual(tm.get_dirty_fields(), {
            'boolean': True,
            'characters': ''
        })

        # resetting them to original values should unflag
        tm.boolean = True
        self.assertEqual(tm.get_dirty_fields(), {
            'characters': ''
        })

    def test_sweeping(self):
        tm = TestModel()
        tm.boolean = False
        tm.characters = 'testing'
        self.assertEqual(tm.get_dirty_fields(), {
            'boolean': True,
            'characters': ''
        })
        tm.save()
        self.assertEqual(tm.get_dirty_fields(), {})

    def test_relationship_option_for_foreign_key(self):
        tm1 = TestModel.objects.create()
        tm2 = TestModel.objects.create()
        tm = TestModelWithForeignKey.objects.create(fkey=tm1)

        # initial state shouldn't be dirty
        self.assertEqual(tm.get_dirty_fields(), {})

        # Default dirty check is not taking foreignkeys into account
        tm.fkey = tm2
        self.assertEqual(tm.get_dirty_fields(), {})

        # But if we use 'check_relationships' param, then we have to.
        self.assertEqual(tm.get_dirty_fields(check_relationship=True), {
            'fkey': tm1.pk
        })

    def test_relationship_option_for_one_to_one_field(self):
        tm1 = TestModel.objects.create()
        tm2 = TestModel.objects.create()
        tm = TestModelWithOneToOneField.objects.create(o2o=tm1)

        # initial state shouldn't be dirty
        self.assertEqual(tm.get_dirty_fields(), {})

        # Default dirty check is not taking onetoone fields into account
        tm.o2o = tm2
        self.assertEqual(tm.get_dirty_fields(), {})

        # But if we use 'check_relationships' param, then we have to.
        self.assertEqual(tm.get_dirty_fields(check_relationship=True), {
            'o2o': tm1.pk
        })

    def test_dirty_fields_ignores_the_editable_property_of_fields(self):
        # Non regression test case for bug:
        # https://github.com/smn/django-dirtyfields/issues/17
        tm = TestModelWithNonEditableFields.objects.create()

        # initial state shouldn't be dirty
        self.assertEqual(tm.get_dirty_fields(), {})

        # changing values should flag them as dirty
        tm.boolean = False
        tm.characters = 'testing'
        self.assertEqual(tm.get_dirty_fields(), {
            'boolean': True,
            'characters': ''
        })
        self.assertEqual(tm.get_dirty_fields(check_relationship=True), {
            'boolean': True,
            'characters': ''
        })

        # resetting them to original values should unflag
        tm.boolean = True
        self.assertEqual(tm.get_dirty_fields(), {
            'characters': ''
        })
        self.assertEqual(tm.get_dirty_fields(check_relationship=True), {
            'characters': ''
        })

    def test_mandatory_foreign_key_field_not_initialized_is_not_raising_related_object_exception(self):
        # Non regression test case for bug:
        # https://github.com/smn/django-dirtyfields/issues/26
        self.assertRaises(IntegrityError,
                          TestModelWithForeignKey.objects.create)

    def _get_query_num(self, model_class):
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

    @override_settings(DEBUG=True)  # The test runner sets DEBUG to False. Set to True to enable SQL logging.
    def test_relationship_model_loading_issue(self):
        # Non regression test case for bug:
        # https://github.com/smn/django-dirtyfields/issues/34

        # Query tests with models that are not using django-dirtyfields
        tm1 = OrdinaryTestModel.objects.create()
        tm2 = OrdinaryTestModel.objects.create()
        tmf1 = OrdinaryTestModelWithForeignKey.objects.create(fkey=tm1)
        tmf2 = OrdinaryTestModelWithForeignKey.objects.create(fkey=tm2)

        for tmf in OrdinaryTestModelWithForeignKey.objects.all():
            pk = tmf.pk

        self.assertEqual(self._get_query_num(OrdinaryTestModelWithForeignKey), 1)
        self.assertEqual(self._get_query_num(OrdinaryTestModel), 0)  # should be 0 since we don't access the relationship for now.

        for tmf in OrdinaryTestModelWithForeignKey.objects.all():
            fkey = tmf.fkey  # access the relationship here

        self.assertEqual(self._get_query_num(OrdinaryTestModelWithForeignKey) - 1, 1)
        self.assertEqual(self._get_query_num(OrdinaryTestModel), 2)  # should be 2

        for tmf in OrdinaryTestModelWithForeignKey.objects.select_related('fkey').all():
            fkey = tmf.fkey  # access the relationship here

        self.assertEqual(self._get_query_num(OrdinaryTestModelWithForeignKey) - 2, 1)
        self.assertEqual(self._get_query_num(OrdinaryTestModel) - 2, 0)  # should be 0 since we use `select_related`

        # Query tests with models that are using django-dirtyfields
        tm1 = TestModel.objects.create()
        tm2 = TestModel.objects.create()
        tmf1 = TestModelWithForeignKey.objects.create(fkey=tm1)
        tmf2 = TestModelWithForeignKey.objects.create(fkey=tm2)

        for tmf in TestModelWithForeignKey.objects.all():
            pk = tmf.pk  # we don't need the relationship here

        self.assertEqual(self._get_query_num(TestModelWithForeignKey), 1)
        self.assertEqual(self._get_query_num(TestModel), 0)  # should be 0, was 2 before bug fixing

        for tmf in TestModelWithForeignKey.objects.all():
            fkey = tmf.fkey  # access the relationship here

        self.assertEqual(self._get_query_num(TestModelWithForeignKey) - 1, 1)
        self.assertEqual(self._get_query_num(TestModel), 2)  # should be 0, but the relationship is loaded by DirtyFieldsMixin

        for tmf in TestModelWithForeignKey.objects.select_related('fkey').all():
            dummy = tmf.fkey  # access the relationship here

        self.assertEqual(self._get_query_num(TestModelWithForeignKey) - 2, 1)
        self.assertEqual(self._get_query_num(TestModel) - 2, 0)  # should be 0 since we use `selected_related` (was 2 before)

    def test_relationship_option_for_foreign_key_to_self(self):
        # Non regression test case for bug:
        # https://github.com/smn/django-dirtyfields/issues/22
        tm = TestModelWithSelfForeignKey.objects.create()
        tm1 = TestModelWithSelfForeignKey.objects.create(fkey=tm)

        tm.fkey = tm1
        tm.save()

        # Trying to access an instance was triggering a "RuntimeError: maximum recursion depth exceeded"
        TestModelWithSelfForeignKey.objects.all()[0]

    def test_non_local_fields(self):
        subclass = SubclassModel.objects.create(characters='foo')
        subclass.characters = 'spam'

        self.assertTrue(subclass.is_dirty())
        self.assertDictEqual(subclass.get_dirty_fields(), {'characters': 'foo'})

    def test_decimal_field_correctly_managed(self):
        # Non regression test case for bug:
        # https://github.com/smn/django-dirtyfields/issues/4
        tm = TestModelWithDecimalField.objects.create(decimal_field=Decimal(2.00))

        # initial state shouldn't be dirty
        self.assertFalse(tm.is_dirty())

        tm.decimal_field = 2.0
        self.assertFalse(tm.is_dirty())

        tm.decimal_field = u"2.00"
        self.assertFalse(tm.is_dirty())

    @skip_unless_jsonfield_library
    def test_json_field(self):
        import json
        from .models import JSONFieldModel

        tm = JSONFieldModel.objects.create(json_field={'data': 'dummy_data'})

        # initial state shouldn't be dirty
        self.assertFalse(tm.is_dirty())

        tm.json_field['data'] = 'dummy_data_modified'

        self.assertEqual(tm.get_dirty_fields(), {
            'json_field': {'data': 'dummy_data'}
        })
