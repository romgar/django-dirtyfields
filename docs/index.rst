
Welcome to django-dirtyfields's documentation!
==============================================

``django-dirtyfields`` is a small library for tracking dirty fields on a Django model instance.
Dirty means that a field's in-memory value is different to the value in the database.


Table of Contents:
------------------

.. toctree::
   :maxdepth: 2

   Quickstart <self>
   advanced
   customisation
   contributing
   credits


Quickstart
==========


Install
-------

.. code-block:: bash

    $ pip install django-dirtyfields


Usage
-----

To use ``django-dirtyfields``, you need to:

- Inherit from ``DirtyFieldsMixin`` in the Django model you want to track.

.. code-block:: python

    from django.db import models
    from dirtyfields import DirtyFieldsMixin

    class ExampleModel(DirtyFieldsMixin, models.Model):
        """A simple example model to test dirty fields mixin with"""
        boolean = models.BooleanField(default=True)
        characters = models.CharField(blank=True, max_length=80)

- Use one of these 2 functions on a model instance to know if this instance is dirty, and get the dirty fields:

  * ``is_dirty()``
  * ``get_dirty_fields()``


Example
-------

.. code-block:: python

    >>> model = ExampleModel.objects.create(boolean=True,
                                            characters="first value")
    >>> model.is_dirty()
    False
    >>> model.get_dirty_fields()
    {}

    >>> model.boolean = False
    >>> model.characters = "second value"

    >>> model.is_dirty()
    True
    >>> model.get_dirty_fields()
    {'boolean': True, "characters": "first_value"}


Why would you want this?
------------------------

When using :mod:`django:django.db.models.signals` (:data:`django.db.models.signals.pre_save` especially), it is useful to be able to see what fields have changed or not. A signal could change its behaviour depending on whether a specific field has changed, whereas otherwise, you only could work on the event that the model's :meth:`~django.db.models.Model.save` method had been called.
