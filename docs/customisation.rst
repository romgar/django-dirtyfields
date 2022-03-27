Customisation
=============

Ways to customise the behavior of django-dirtyfields


Checking many-to-many fields.
-----------------------------
**WARNING**: this m2m mode will generate extra queries to get m2m relation values each time you will save your objects.
It can have serious performance issues depending on your project.

By default, dirty functions are not checking many-to-many fields.
They are also a bit special, as a call to ``.add()`` method is directly
saving the related object to the database, thus the instance is never dirty.
If you want to check these relations, you should set ``ENABLE_M2M_CHECK`` to ``True`` in your model inheriting from
``DirtyFieldsMixin``, use ``check_m2m`` parameter and provide the values you want to test against:

.. code-block:: python

    class Many2ManyModel(DirtyFieldsMixin, models.Model):
        ENABLE_M2M_CHECK = True
        m2m_field = models.ManyToManyField(AnotherModel)

.. code-block:: pycon

    >>> model = Many2ManyModel.objects.create()
    >>> related_model = AnotherModel.objects.create()
    >>> model.is_dirty()
    False
    >>> model.m2m_field.add(related_model)
    >>> model.is_dirty()
    False
    >>> model.get_dirty_fields(check_m2m={"m2m_field": {related_model.id}})
    {}
    >>> model.get_dirty_fields(check_m2m={"m2m_field": set()})
    {'m2m_field': set([related_model.id])}


This can be useful when validating forms with m2m relations, where you receive some ids and want to know if your object
in the database needs to be updated with these form values.


Checking a limited set of model fields.
---------------------------------------
If you want to check a limited set of model fields, you should set ``FIELDS_TO_CHECK`` in your model inheriting from ``DirtyFieldsMixin``:

.. code-block:: python

    class ModelWithSpecifiedFields(DirtyFieldsMixin, models.Model):
        boolean1 = models.BooleanField(default=True)
        boolean2 = models.BooleanField(default=True)
        FIELDS_TO_CHECK = ["boolean1"]

.. code-block:: pycon

    >>> model = ModelWithSpecifiedFields.objects.create()

    >>> model.boolean1 = False
    >>> model.boolean2 = False

    >>> model.get_dirty_fields()
    {'boolean1': True}


This can be used in order to increase performance.


Custom comparison function
----------------------------
By default, ``dirtyfields`` compare the value between the database and the memory on a naive way (``==``).
After some issues (with timezones for example), a customisable comparison logic has been added.
You can now define how you want to compare 2 values by passing a function on DirtyFieldsMixin:

.. code-block:: python

    from django.db import models
    from dirtyfields import DirtyFieldsMixin

    def your_function((new_value, old_value, param1):
        # Your custom comparison code here
        return new_value == old_value

    class YourModel(DirtyFieldsMixin, models.Model):
        compare_function = (your_function, {"param1": 5})


Have a look at ``dirtyfields.compare`` module to get some examples.


Custom value normalisation function
-----------------------------------
By default, ``dirtyfields`` reports on the dirty fields as is. If a date field was changed
the result of ``get_dirty_fields()`` will return the current and saved datetime object.
In some cases it is useful to normalise those values, e.g., when wanting ot save the diff data as a json dataset in a database.
The default behaviour of using values as is can be changed by providing a ``normalise_function``
in your model. That function can evaluate the value's type and rewrite it accordingly.

This example shows the usage of the normalise function, with an extra paramter of a user's timezone
being passed as well:

.. code-block:: python

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
        return "Europe/London"

    class YourModel(DirtyFieldsMixin, models.Model):
        normalise_function = (your_normalise_function,
                              {"timezone": get_user_timezone()})
