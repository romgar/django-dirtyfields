Django Dirty Fields
===================

Tracking dirty fields on a Django model instance.

::

    $ pip install django-dirtyfields

or if you're interested in developing it

::

    $ virtualenv --no-site-packages ve/
    $ source ve/bin/activate
    (ve)$ pip install -r requirements.pip
    (ve)$ python setup.py develop
    (ve)$ cd example_app && ./manage.py test testing_app

Makes a Mixing available that will give you the methods:

 * is\_dirty()
 * get\_dirty\_fields()
    

Using the Mixin in the Model
----------------------------

::
    
    from django.db import models
    from dirtyfields import DirtyFieldsMixin

    class TestModel(DirtyFieldsMixin, models.Model):
        """A simple test model to test dirty fields mixin with"""
        boolean = models.BooleanField(default=True)
        characters = models.CharField(blank=True, max_length=80)
    

Using it in the shell
---------------------

::

    (ve)$ ./manage.py shell
    >>> from testing_app.models import TestModel
    >>> tm = TestModel(boolean=True,characters="testing")
    >>> tm.save()
    >>> tm.is_dirty()
    False
    >>> tm.get_dirty_fields()
    {}
    >>> tm.boolean = False
    >>> tm.is_dirty()
    True
    >>> tm.get_dirty_fields()
    {'boolean': True}
    >>> tm.characters = "have changed"
    >>> tm.is_dirty()
    True
    >>> tm.get_dirty_fields()
    {'boolean': True, 'characters': 'testing'}
    >>> tm.save()
    >>> tm.is_dirty()
    False
    >>> tm.get_dirty_fields()
    {}
    >>> 

Why would you want this?
------------------------

When using signals_, especially pre_save_, it is useful to be able to see what fields have changed or not. A signal could change its behaviour depending on whether a specific field has changed, whereas otherwise, you only could work on the event that the model's `save()` method had been called.

Credits
-------

This code has largely be adapted from what was made available at `Stack Overflow`_.

.. _Stack Overflow: http://stackoverflow.com/questions/110803/dirty-fields-in-django
.. _signals: http://docs.djangoproject.com/en/1.2/topics/signals/
.. _pre_save: http://docs.djangoproject.com/en/1.2/ref/signals/#django.db.models.signals.pre_save

