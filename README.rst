===================
Django Dirty Fields
===================

.. image:: https://badges.gitter.im/Join%20Chat.svg
   :alt: Join the chat at https://gitter.im/romgar/django-dirtyfields
   :target: https://gitter.im/romgar/django-dirtyfields?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
.. image:: https://img.shields.io/pypi/v/django-dirtyfields.svg
   :target: https://pypi.org/project/django-dirtyfields/
.. image:: https://travis-ci.org/romgar/django-dirtyfields.svg?branch=develop
   :target: https://travis-ci.org/romgar/django-dirtyfields?branch=develop
.. image:: https://coveralls.io/repos/romgar/django-dirtyfields/badge.svg?branch=develop
   :target: https://coveralls.io/r/romgar/django-dirtyfields?branch=develop
.. image:: https://readthedocs.org/projects/django-dirtyfields/badge/?version=develop
   :target: https://django-dirtyfields.readthedocs.org/en/develop/?badge=develop

Tracking dirty fields on a Django model instance.
Dirty means that field in-memory and database values are different.

This package is compatible and tested with the following Python & Django versions:



+---------------+------------------------------------------------------+
| Django        | Python                                               |
+===============+======================================================+
| 1.11          | 3.6, 3.7 (as of 1.11.17)                             |
+---------------+------------------------------------------------------+
| 2.0, 2.1      | 3.6, 3.7                                             |
+---------------+------------------------------------------------------+
| 2.2           | 3.6, 3.7, 3.8 (as of 2.2.8), 3.9 (as of 2.2.17)      |
+---------------+------------------------------------------------------+
| 3.0           | 3.6, 3.7, 3.8, 3.9 (as of 3.0.11)                    |
+---------------+------------------------------------------------------+
| 3.1           | 3.6, 3.7, 3.8, 3.9 (as of 3.1.3)                     |
+---------------+------------------------------------------------------+



Install
=======

.. code-block:: bash

   $ pip install django-dirtyfields


Usage
=====

To use ``django-dirtyfields``, you need to:

- Inherit from ``DirtyFieldsMixin`` in the Django model you want to track.

  .. code-block:: python

    from django.db import models
    from dirtyfields import DirtyFieldsMixin

    class ModelTest(DirtyFieldsMixin, models.Model):
        """A simple test model to test dirty fields mixin with"""
        boolean = models.BooleanField(default=True)
        characters = models.CharField(blank=True, max_length=80)

- Use one of these 2 functions on a model instance to know if this instance is dirty, and get the dirty fields:

  * is\_dirty()
  * get\_dirty\_fields()


Example
-------

.. code-block:: python

    >>> from tests.models import ModelTest
    >>> tm = ModelTest.objects.create(boolean=True,characters="testing")
    >>> tm.is_dirty()
    False
    >>> tm.get_dirty_fields()
    {}

    >>> tm.boolean = False

    >>> tm.is_dirty()
    True
    >>> tm.get_dirty_fields()
    {'boolean': True}


Consult the `full documentation <https://django-dirtyfields.readthedocs.org/en/develop/>`_ for more informations.



