===================
Django Dirty Fields
===================

.. image:: https://badges.gitter.im/Join%20Chat.svg
   :alt: Join the chat at https://gitter.im/romgar/django-dirtyfields
   :target: https://gitter.im/romgar/django-dirtyfields?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
.. image:: https://travis-ci.org/romgar/django-dirtyfields.svg?branch=develop
    :target: https://travis-ci.org/romgar/django-dirtyfields?branch=develop
.. image:: https://coveralls.io/repos/romgar/django-dirtyfields/badge.svg?branch=develop
   :target: https://coveralls.io/r/romgar/django-dirtyfields?branch=develop
.. image:: http://readthedocs.org/projects/django-dirtyfields/badge/?version=develop
   :target: http://django-dirtyfields.readthedocs.org/en/develop/?badge=develop

Tracking dirty fields on a Django model instance.
Dirty means that field in-memory and database values are different.

`Full documentation <http://django-dirtyfields.readthedocs.org/en/develop/>`_

Install
=======

::

    $ pip install django-dirtyfields


Usage
=====

To use ``django-dirtyfields``, you need to:

- Inherit from ``DirtyFieldMixin`` in the Django model you want to track.

::
    
    from django.db import models
    from dirtyfields import DirtyFieldsMixin

    class TestModel(DirtyFieldsMixin, models.Model):
        """A simple test model to test dirty fields mixin with"""
        boolean = models.BooleanField(default=True)
        characters = models.CharField(blank=True, max_length=80)

- Use one of these 2 functions on a model instance to know if this instance is dirty, and get the dirty fields:

    * is\_dirty()
    * get\_dirty\_fields()


Example
-------

::

    >>> from tests.models import TestModel
    >>> tm = TestModel.objects.create(boolean=True,characters="testing")
    >>> tm.is_dirty()
    False
    >>> tm.get_dirty_fields()
    {}

    >>> tm.boolean = False

    >>> tm.is_dirty()
    True
    >>> tm.get_dirty_fields()
    {'boolean': True}


Consult the `full documentation <http://django-dirtyfields.readthedocs.org/en/develop/>`_ for more informations.



