from django.test import TestCase
from .models import (TestModel, TestModelWithForeignKey,
                    TestModelWithNonEditableFields, TestModelWithOneToOneField)


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
