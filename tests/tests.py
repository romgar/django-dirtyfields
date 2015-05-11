import re
from django.conf import settings
from django.db import connection
from django.db import IntegrityError
from django.test import TestCase
from .models import (TestModel, TestModelWithForeignKey,
                    TestModelWithNonEditableFields, TestModelWithOneToOneField,
                    OrdinaryTestModel, OrdinaryTestModelWithForeignKey)
                    

class DirtyFieldsMixinTestCase(TestCase):
    
    @classmethod
    def setUpClass(cls):
        super(DirtyFieldsMixinTestCase, cls).setUpClass()
        # The test runner sets DEBUG to False. Set to True to enable SQL logging.
        settings.DEBUG = True
    
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
            'fkey': tm1
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
            'o2o': tm1
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
                          
    def test_relationship_model_loading_issue(self):
        
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
        self.assertEqual(self._get_query_num(OrdinaryTestModel) - 2, 0)  # since we use `select_related`
        
        tm1 = TestModel.objects.create()
        tm2 = TestModel.objects.create()
        tmf1 = TestModelWithForeignKey.objects.create(fkey=tm1)
        tmf2 = TestModelWithForeignKey.objects.create(fkey=tm2)
        
        for tmf in TestModelWithForeignKey.objects.all():
            pk = tmf.pk  # we don't need the relationship here
            
        self.assertEqual(self._get_query_num(TestModelWithForeignKey), 1)
        self.assertEqual(self._get_query_num(TestModel), 2)  # should be 0, but the relationship is loaded by DirtyFieldsMixin
        
        for tmf in TestModelWithForeignKey.objects.select_related('fkey').all():
            fkey = tmf.fkey  # access the relationship here
        
        self.assertEqual(self._get_query_num(TestModelWithForeignKey) - 1, 1)
        self.assertEqual(self._get_query_num(TestModel) - 2, 2)  # should be 0 since we use `selected_related`
