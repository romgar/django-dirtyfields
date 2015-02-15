from django.test import TestCase

from testing_app.models import TestModel, TestModelWithForeignKey, TestModelWithManyToMany


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

        # Default dirty check is not taking relationships into account
        tm.fkey = tm2
        self.assertEqual(tm.get_dirty_fields(), {})

        # But if we use 'check_relationships' param, then we have to.
        self.assertEqual(tm.get_dirty_fields(check_relationship=True), {
            'fkey': tm1.id
        })

    def test_relationship_option_for_many_to_many(self):
        tm1 = TestModel.objects.create()
        tm2 = TestModel.objects.create()
        tm = TestModelWithManyToMany.objects.create()
        # import pdb; pdb.set_trace()
        # initial state shouldn't be dirty
        self.assertEqual(tm.get_dirty_fields(), {})

        # Default dirty check is not taking relationships into account
        tm.m2m.add(tm1)
        self.assertEqual(tm.get_dirty_fields(check_relationship=True), {
            'm2m': []
        })

        tm.m2m.add(tm2)
        self.assertEqual(tm.get_dirty_fields(check_relationship=True), {
            'm2m': [tm1.id]
        })
