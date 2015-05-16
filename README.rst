Django Dirty Fields
===================

.. image:: https://badges.gitter.im/Join%20Chat.svg
   :alt: Join the chat at https://gitter.im/smn/django-dirtyfields
   :target: https://gitter.im/smn/django-dirtyfields?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
.. image:: https://travis-ci.org/smn/django-dirtyfields.svg?branch=develop
    :target: https://travis-ci.org/smn/django-dirtyfields
.. image:: https://coveralls.io/repos/smn/django-dirtyfields/badge.svg
   :target: https://coveralls.io/r/smn/django-dirtyfields

Tracking dirty fields on a Django model instance.

::

    $ pip install django-dirtyfields


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


Checking foreign key fields.
----------------------------
By default, dirty functions are not checking foreign keys. If you want to also take these relationships into account, use ``check_relationship`` parameter:

::

    (ve)$ ./manage.py shell
    >>> from testing_app.models import TestModel
    >>> tm = TestModel(fkey=obj1)
    >>> tm.save()
    >>> tm.is_dirty()
    False
    >>> tm.get_dirty_fields()
    {}
    >>> tm.fkey = obj2
    >>> tm.is_dirty()
    False
    >>> tm.is_dirty(check_relationship=True)
    True
    >>> tm.get_dirty_fields()
    {}
    >>> tm.get_dirty_fields(check_relationship=True)
    {'fkey': obj1}


Why would you want this?
------------------------

When using signals_, especially pre_save_, it is useful to be able to see what fields have changed or not. A signal could change its behaviour depending on whether a specific field has changed, whereas otherwise, you only could work on the event that the model's `save()` method had been called.


Contributing
============
If you're interested in developing it, you can launch project tests on that way:

::
    $ pip install tox
    $ pip install -e .
    $ tox


Credits
-------

This code has largely be adapted from what was made available at `Stack Overflow`_.

.. _Stack Overflow: http://stackoverflow.com/questions/110803/dirty-fields-in-django
.. _signals: http://docs.djangoproject.com/en/1.2/topics/signals/
.. _pre_save: http://docs.djangoproject.com/en/1.2/ref/signals/#django.db.models.signals.pre_save

