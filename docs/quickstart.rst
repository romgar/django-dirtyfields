Quickstart
==========


.. include:: description.rst


Installation
------------

.. code-block:: bash

    $ pip install django-dirtyfields


Usage
-----

To use ``django-dirtyfields``, you need to:

- Inherit from the ``DirtyFieldsMixin`` class in the Django model you want to track dirty fields.

.. code-block:: python

    from django.db import models
    from dirtyfields import DirtyFieldsMixin

    class ExampleModel(DirtyFieldsMixin, models.Model):
        """A simple example model to test dirtyfields with"""
        characters = models.CharField(max_length=80)

- Use one of these 2 functions on a model instance to know if this instance is dirty, and get the dirty fields:

  * ``is_dirty()``
  * ``get_dirty_fields()``


Example
-------

.. code-block:: pycon

    >>> model = ExampleModel.objects.create(characters="first value")
    >>> model.is_dirty()
    False
    >>> model.get_dirty_fields()
    {}
    >>> model.characters = "second value"
    >>> model.is_dirty()
    True
    >>> model.get_dirty_fields()
    {'characters': 'first_value'}


Why would you want this?
------------------------

When using :mod:`django:django.db.models.signals` (:data:`django.db.models.signals.pre_save` especially),
it is useful to be able to see what fields have changed or not. A signal could change its behaviour
depending on whether a specific field has changed, whereas otherwise, you only could work on the event
that the model's :meth:`~django.db.models.Model.save` method had been called.
