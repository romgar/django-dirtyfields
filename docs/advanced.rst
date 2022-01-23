Advanced Usage
==============


Verbose mode
------------
By default, when you use ``get_dirty_fields()`` function, if there are dirty fields, only the old value is returned.
You can use ``verbose`` option to return the saved and current value:

.. code-block:: python

    >>> model.get_dirty_fields()
    {'boolean': True, 'characters': 'first_value'}
    >>> model.get_dirty_fields(verbose=True)
    {
        'boolean': {'saved': True, 'current': False},
        'characters': {'saved': "first value", 'current': 'second value'}
    }


Checking foreign key fields.
----------------------------
By default, dirty functions are not checking foreign keys. If you want to also take these relationships into account,
use ``check_relationship`` parameter:

.. code-block:: python

    class ForeignKeyModel(DirtyFieldsMixin, models.Model):
        fkey = models.ForeignKey(AnotherModel, on_delete=models.CASCADE)

    >>> model = ForeignKeyModel.objects.create(fkey=obj1)
    >>> model.is_dirty()
    False

    >>> model.fkey = obj2

    >>> model.is_dirty()
    False
    >>> model.is_dirty(check_relationship=True)
    True

    >>> model.get_dirty_fields()
    {}
    >>> model.get_dirty_fields(check_relationship=True)
    {'fkey': 1}


Saving dirty fields.
--------------------
If you want to only save dirty fields from an instance in the database (only these fields will be involved in SQL query),
you can use ``save_dirty_fields()`` method.

Warning: This calls the ``save()`` method internally so will trigger the same signals as normally calling the ``save()`` method.

.. code-block:: python

    >>> model.get_dirty_fields()
    {'boolean': True, 'characters': 'first_value'}
    >>> model.save_dirty_fields()
    >>> model.get_dirty_fields()
    {}
