ChangeLog
=========

.. _unreleased:

unreleased
------


.. _v1.9.0:

1.9.0 (2022-11-07)
------------------

*New:*
    - Confirm support for Python 3.11
    - Confirm support for Django 4.1
    - Drop support for Django 1.11

*Changed:*
    - The method :code:`get_dirty_fields()` now returns only the file name for FileFields.
      This is to improve performance, since the entire :code:`FieldFile` object will no longer
      be copied when Model instances are initialized and saved. (#203)

*Bugfix:*
    - The method :code:`save_dirty_fields()` can now be called on Model instances that have not been
      saved to the Database yet. In this case all fields will be considered dirty, and all will be
      saved to the Database. Previously doing this would result in an Exception being raised. (#200)


.. _v1.8.2:

1.8.2 (2022-07-16)
------------------

*Documentation:*
    - General improvements to content and generation of Documentation (#197).


.. _v1.8.1:

1.8.1 (2022-03-07)
------------------

*Documentation:*
    - Document limitations when using dirtyfields and database transactions (#148).
    - Document how to use a Proxy Model to avoid performance impact (#132).


.. _v1.8.0:

1.8.0 (2022-01-22)
------------------

*New:*
    - Confirm support of Python 3.10
    - Confirm support of Django 4.0
    - Drop support for Python 3.6

*Tests*
    - Run CI tests on Github Actions since travis-ci.org has been shutdown.


.. _v1.7.0:

1.7.0 (2021-05-02)
------------------

*New:*
    - Provide programmatically accessible package version number. Use :code:`dirtyfields.__version__` for a string,
      :code:`dirtyfields.VERSION` for a tuple.
    - Build and publish a wheel to PyPI.

*Changed:*
    - Only look at concrete fields when determining dirty fields.
    - Migrate package metadata from setup.py to setup.cfg and specify the PEP-517 build-backend to use with the project.

*Bugfix:*
    - Fixed a :code:`KeyError` that happened when saving a Model with :code:`update_fields` specified after updating a
      field value with an :code:`F` object (#118).

.. _v1.6.0:

1.6.0 (2021-04-07)
------------------

*New:*
    - Confirm support of Django 3.2

*Changed:*
    - Remove pytz as a dependency.

.. _v1.5.0:

1.5.0 (2021-01-15)
------------------

*New:*
    - Drop support of Python 2.7
    - Drop support of Python 3.5
    - Confirm support of Python 3.8
    - Confirm support of Python 3.9
    - Confirm support of Django 3.0
    - Confirm support of Django 3.1

.. _v1.4.1:

1.4.1 (2020-11-28)
------------------

*Bugfix:*
    - Fixes an issue when :code:`refresh_from_db` was called with the :code:`fields` argument, the dirty state for all
      fields would be reset, even though only the fields specified are reloaded from the database. Now only the reloaded
      fields will have their dirty state reset (#154).
    - Fixes an issue where accessing a deferred field would reset the dirty state for all fields (#154).

.. _v1.4:

1.4 (2020-04-11)
----------------

*New:*
    - Drop support of Python 3.4
    - Drop support of Django 1.8
    - Drop support of Django 1.9
    - Drop support of Django 1.10
    - Confirm support of Python 3.7
    - Confirm support of Django 2.0
    - Confirm support of Django 2.1
    - Confirm support of Django 2.2

*Bugfix:*
    - Fixes tests for Django 2.0
    - :code:`refresh_from_db` is now properly resetting dirty fields.
    - Adds :code:`normalise_function` to provide control on how dirty values are stored

.. _v1.3.1:

1.3.1 (2018-02-28)
------------------

*New:*

    - Updates python classifier in setup file (#116). Thanks amureki.
    - Adds PEP8 validation in travisCI run (#123). Thanks hsmett.

*Bugfix:*

    - Avoids :code:`get_deferred_fields` to be called too many times on :code:`_as_dict` (#115). Thanks benjaminrigaud.
    - Respects :code:`FIELDS_TO_CHECK` in `reset_state` (#114). Thanks bparker98.

.. _v1.3:

1.3 (2017-08-23)
----------------

*New:*

    - Drop support for unsupported Django versions: 1.4, 1.5, 1.6 and 1.7 series.
    - Fixes issue with verbose mode when the object has not been yet saved in the database (MR #99). Thanks vapkarian.
    - Add test coverage for Django 1.11.
    - A new attribute :code:`FIELDS_TO_CHECK` has been added to :code:`DirtyFieldsMixin` to specify a limited set of fields to check.

*Bugfix:*

    - Correctly handle :code:`ForeignKey.db_column` :code:`{}_id` in :code:`update_fields`. Thanks Hugo Smett.
    - Fixes #111: Eliminate a memory leak.
    - Handle deferred fields in :code:`update_fields`


.. _v1.2.1:

1.2.1 (2016-11-16)
------------------

*New:*

    - :code:`django-dirtyfields` is now tested with PostgreSQL, especially with specific fields

*Bugfix:*

    - Fixes #80: Use of :code:`Field.rel` raises warnings from Django 1.9+
    - Fixes #84: Use :code:`only()` in conjunction with 2 foreign keys triggers a recursion error
    - Fixes #77: Shallow copy does not work with Django 1.9's JSONField
    - Fixes #88: :code:`get_dirty_fields` on a newly-created model does not work if pk is specified
    - Fixes #90: Unmark dirty fields only listed in :code:`update_fields`


.. _v1.2:

1.2 (2016-08-11)
----------------

*New:*

    - :code:`django-dirtyfields` is now compatible with Django 1.10 series (deferred field handling has been updated).


.. _v1.1:

1.1 (2016-08-04)
----------------

*New:*

    - A new attribute :code:`ENABLE_M2M_CHECK` has been added to :code:`DirtyFieldsMixin` to enable/disable m2m check
      functionality. This parameter is set to :code:`False` by default.
      IMPORTANT: backward incompatibility with v1.0.x series. If you were using :code:`check_m2m` parameter to
      check m2m relations, you should now add :code:`ENABLE_M2M_CHECK = True` to these models inheriting from
      :code:`DirtyFieldsMixin`. Check the documentation to see more details/examples.


.. _v1.0.1:

1.0.1 (2016-07-25)
------------------

*Bugfix:*

    - Fixing a bug preventing :code:`django-dirtyfields` to work properly on models with custom primary keys.


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
    - Adding compatibility for old _meta API, deprecated in Django `1.10` version and now replaced by an official API.
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

*Bugfix:*

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
