ChangeLog
=========


.. _v1.0:

1.0 (2016-06-26)
----------------

After several years of existence, django-dirty-fields is mature enough to switch to 1.X version.
There is a backward-incompatibility on this version. Please read careful below.

*New:*

    - IMPORTANT: :code:`get_dirty_fields` is now more consistent for models not yet saved in the database.
      :code:`get_dirty_fields` is, in that situation, always returning ALL fields, where it was before returning
      various results depending on how you initialised your model.
      It may affect you specially if you are using :code:`get_dirty_fields` in a :code:`pre_save` receiver.
      See more details at https://github.com/romgar/django-dirtyfields/issues/65.
    - Adding compatibility for old _meta API, deprecated in `1.10` version and now replaced by an official API.
    - General test cleaning.


.. _v0.9:

0.9 (2016-06-18)
----------------

*New:*

    - Adding Many-to-Many fields comparison method :code:`check_m2m` in :code:`DirtyFieldsMixin`.
    - Adding :code:`verbose` parameter in :code:`get_dirty_fields` method to get old AND new field values.


.. _v0.8.2:

0.8.2 (2016-03-19)
------------------

*New:*

    - Adding field comparison method :code:`compare_function` in :code:`DirtyFieldsMixin`.
    - Also adding a specific comparison function :code:`timezone_support_compare` to handle different Datetime situations.


.. _v0.8.1:

0.8.1 (2015-12-08)
------------------

*bugfix:*

    - Not comparing fields that are deferred (:code:`only` method on :code:`QuerySet`).
    - Being more tolerant when comparing values that can be on another type than expected.



.. _v0.8:

0.8 (2015-10-30)
----------------

*New:*

    - Adding :code:`save_dirty_fields` method to save only dirty fields in the database.


.. _v0.7:

0.7 (2015-06-18)
----------------

*New:*

    - Using :code:`copy` to properly track dirty fields on complex fields.
    - Using :code:`py.test` for tests launching.


.. _v0.6.1:

0.6.1 (2015-06-14)
------------------

*Bugfix:*

    - Preventing django db expressions to be evaluated when testing dirty fields (#39).


.. _v0.6:

0.6 (2015-06-11)
----------------

*New:*

    - Using :code:`to_python` to avoid false positives when dealing with model fields that internally convert values (#4)

*Bugfix:*

    - Using :code:`attname` instead of :code:`name` on fields to avoid massive useless queries on ForeignKey fields (#34). For this kind of field, :code:`get_dirty_fields()` is now returning instance id, instead of instance itself.


.. _v0.5:

0.5 (2015-05-06)
----------------

*New:*

    - Adding code compatibility for python3,
    - Launching travis-ci tests on python3,
    - Using :code:`tox` to launch tests on Django 1.5, 1.6, 1.7 and 1.8 versions,
    - Updating :code:`runtests.py` test script to run properly on every Django version.

*Bugfix:*

    - Catching :code:`Error` when trying to get foreign key object if not existing (#32).


.. _v0.4.1:

0.4.1 (2015-04-08)
------------------

*Bugfix:*

    - Removing :code:`model_to_form` to avoid bug when using models that have :code:`editable=False` fields.


.. _v0.4:

0.4 (2015-03-31)
----------------

*New:*

    - Adding :code:`check_relationship` parameter on :code:`is_dirty` and :code:`get_dirty_field` methods to also check foreign key values.
