
Welcome to django-dirtyfields's documentation!
==============================================

Tracking dirty fields on a Django model instance.
Dirty means that field in-memory and database values are different.

`Source code <https://github.com/romgar/django-dirtyfields/>`_

Install
=======

::

    $ pip install django-dirtyfields


Usage
=====

To use ``django-dirtyfields``, you need to:

- Inherit from ``DirtyFieldsMixin`` in the Django model you want to track.

::

    from django.db import models
    from dirtyfields import DirtyFieldsMixin

    class ModelTest(DirtyFieldsMixin, models.Model):
        """A simple test model to test dirty fields mixin with"""
        boolean = models.BooleanField(default=True)
        characters = models.CharField(blank=True, max_length=80)

- Use one of these 2 functions on a model instance to know if this instance is dirty, and get the dirty fields:

    * is\_dirty()
    * get\_dirty\_fields()


Examples
========

::

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


Checking foreign key fields.
----------------------------
By default, dirty functions are not checking foreign keys. If you want to also take these relationships into account, use ``check_relationship`` parameter:

::

    >>> from tests.models import ModelTest
    >>> tm = ModelTest.objects.create(fkey=obj1)
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
    {'fkey': 1}


Checking many-to-many fields.
----------------------------
By default, dirty functions are not checking many-to-many fields. They are also a bit special, as a call to `.add()` method is directly
saving the related object to the database, thus the instance is never dirty.
If you want to check these relations, you should set ``ENABLE_M2M_CHECK`` to ``True`` in your model inheriting from
``DirtyFieldsMixin``, use ``check_m2m`` parameter and provide the values you want to test against:

::

    class Many2ManyModelTest(DirtyFieldsMixin, models.Model):
        ENABLE_M2M_CHECK = True
        m2m_field = models.ManyToManyField(AnotherModel)

    >>> from tests.models import Many2ManyModelTest
    >>> tm = Many2ManyModelTest.objects.create()
    >>> tm2 = ModelTest.objects.create()
    >>> tm.is_dirty()
    False
    >>> tm.m2m_field.add(tm2)
    >>> tm.is_dirty()
    False
    >>> tm.get_dirty_fields(check_m2m={'m2m_field': set([tm2.id])})
    {}
    >>> tm.get_dirty_fields(check_m2m={'m2m_field': set(["dummy_value"])})
    {'m2m_field': set([tm2.id])}


This can be useful when validating forms with m2m relations, where you receive some ids and want to know if your object
in the database needs to be updated with these form values.

**WARNING**: this m2m mode will generate extra queries to get m2m relation values each time you will save your objects.
It can have serious performance issues depending on your project.


Checking a limited set of model fields.
-------------------------------------
If you want to check a limited set of model fields, you should set ``FIELDS_TO_CHECK`` in your model inheriting from ``DirtyFieldsMixin``:

::

    class ModelWithSpecifiedFieldsTest(DirtyFieldsMixin, models.Model):
        boolean1 = models.BooleanField(default=True)
        boolean2 = models.BooleanField(default=True)
        FIELDS_TO_CHECK = ['boolean1']

    >>> from tests.models import ModelWithSpecifiedFieldsTest
    >>> tm = ModelWithSpecifiedFieldsTest.objects.create()

    >>> tm.boolean1 = False
    >>> tm.boolean2 = False

    >>> tm.get_dirty_fields()
    {'boolean1': True}


This can be used in order to increase performance.


Saving dirty fields.
----------------------------
If you want to only save dirty fields from an instance in the database (only these fields will be involved in SQL query), you can use ``save_dirty_fields`` method.

Warning: this ``save_dirty_fields`` method will trigger the same signals as django default ``save`` method.
But, in django 1.4.22-, as we are using under the hood an ``update`` method, we need to manually send these signals, so be aware that only ``sender`` and ``instance`` arguments are passed to the signal in that context.

::

    >>> tm.get_dirty_fields()
    {'fkey': 1}
    >>> tm.save_dirty_fields()
    >>> tm.get_dirty_fields()
    {}

Verbose mode
----------------------------
By default, when you use ``get_dirty_fields`` function, if there are dirty fields, only the old value is returned.
You can use ``verbose`` option to have more informations, for now a dict with old and new value:

::

    >>> tm.get_dirty_fields()
    {'fkey': 1}
    >>> tm.get_dirty_fields(verbose=True)
    {'fkey': {'saved': 1, 'current': 3}}


Custom comparison function
----------------------------
By default, ``dirtyfields`` compare the value between the database and the memory on a naive way (``==``).
After some issues (with timezones for example), a customisable comparison logic has been added.
You can now define how you want to compare 2 values by passing a function on DirtyFieldsMixin:

::

    from django.db import models
    from dirtyfields import DirtyFieldsMixin

    def your_function((new_value, old_value, param1):
        # Your custom comparison code here
        return new_value == old_value

    class ModelTest(DirtyFieldsMixin, models.Model):
        compare_function = (your_function, {'param1': 5})


Have a look at ``dirtyfields.compare`` module to get some examples.

Custom value normalisation function
----------------------------
By default, ``dirtyfields`` reports on the dirty fields as is. If a date field was changed
the result of ``get_dirty_fields`` will return the current and saved datetime object.
In some cases it is useful to normalise those values, e.g., when wanting ot save the diff data as a json dataset in a database.
The default behaviour of using values as is can be changed by providing a ``normalise_function``
in your model. That function can evaluate the value's type and rewrite it accordingly.

This example shows the usage of the normalise function, with an extra paramter of a user's timezone
being passed as well:

::
    import pytz
    import datetime
    from django.db import models
    from dirtyfields import DirtyFieldsMixin

    def your_normalise_function(value, timezone=None):
        if isinstance(value, (datetime.datetime, datetime.date)):
            if timezone:
                return pytz.timezone(timezone).localize(value).isoformat()
            else:
                return value.isoformat()
        else:
            return value

    def get_user_timezone():
        return 'Europe/London'

    class ModelTest(DirtyFieldsMixin, models.Model):
        normalise_function = (your_normalise_function, {'timezone': get_user_timezone()})


Why would you want this?
========================

When using :mod:`django:django.db.models.signals` (:data:`django.db.models.signals.pre_save` especially), it is useful to be able to see what fields have changed or not. A signal could change its behaviour depending on whether a specific field has changed, whereas otherwise, you only could work on the event that the model's :meth:`~django.db.models.Model.save` method had been called.


.. include:: contributing.rst
.. include:: credits.rst

Table of Contents:
==================

.. toctree::
   :maxdepth: 2

   contributing
   credits


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

