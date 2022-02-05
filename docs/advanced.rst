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


Performance Impact
------------------

Using ``DirtyFieldsMixin`` in your Model will have a (normally small) performance impact even when you don't call
any of ``DirtyFieldsMixin``'s methods. This is because ``DirtyFieldsMixin`` needs to captures the state of the Model
when it is initialized and when it is saved, so that ``DirtyFieldsMixin`` can later determine if the fields are dirty.

Using a Proxy Model to reduce Performance Impact
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you only use ``DirtyFieldsMixin``'s methods in some places of you project but not all, you can eliminate the
performance impact in the places you don't use them by inheriting from ``DirtyFieldsMixin`` in a `Proxy Model`_.

.. _Proxy Model: https://docs.djangoproject.com/en/dev/topics/db/models/#proxy-models

For example have your regular Model without ``DirtyFieldsMixin``:

.. code-block:: python

    class Foo(models.Model):
        ...

Use this Model class when you don't need to track dirtyfields.

Then have a Proxy Model which includes ``DirtyFieldsMixin``:

.. code-block:: python

     class FooWithDirtyFields(DirtyFieldsMixin, FooModel):
         class Meta:
             proxy = True

Use this Model class when you do want dirtyfields to be tracked.


Database Transactions Limitations
---------------------------------
There is currently a limitation when using dirtyfields and database transactions.
If your code saves Model instances inside a ``transaction.atomic()`` block, and the transaction is rolled back,
then the Model instance's ``is_dirty()`` method will return ``False`` when it should return ``True``.
The ``get_dirty_fields()`` method will also return the wrong thing in the same way.

This is because after the ``save()`` method is called, the instance's dirty state is reset because it thinks it has
successfully saved to the database. Then when the transaction rolls back, the database is reset back to the original value.
At this point this Model instance thinks it is not dirty when it actually is.
Here is a code example to illustrate the problem:

.. code-block:: python

    # first create a model
    model = ExampleModel.objects.create(boolean=True, characters="first")
    # then make an edit in-memory, model becomes dirty
    model.characters = "second"
    assert model.is_dirty()
    # then attempt to save the model in a transaction
    try:
        with transaction.atomic():
            model.save()
            # no longer dirty because save() has been called,
            # BUT we are still in a transaction ...
            assert not model.is_dirty()
            # force a transaction rollback
            raise DatabaseError("pretend something went wrong")
    except DatabaseError:
        pass

    # Here is the problem:
    # value in DB is still "first" but model does not think its dirty,
    # because in-memory value is still "second"
    assert model.characters == "second"
    assert not model.is_dirty()


This simplest workaround to this issue is to call ``model.refresh_from_db()`` if the transaction is rolled back.
Or you can manually restore the fields that were edited in-memory.
