ChangeLog
=========


.. _v0.6.1:

0.6.1 (2015-06-14)
------------------

*Bugfix:*

    - Preventing django db expressions to be evaluated when testing dirty fields (#39).


.. _v0.6:

0.6 (2015-06-11)
------------------

*New:*

    - Using :code:`to_python` to avoid false positives when dealing with model fields that internally convert values (#4)

*Bugfix:*

    - Using :code:`attname` instead of :code:`name` on fields to avoid massive useless queries on ForeignKey fields (#34). For this kind of field, :code:`get_dirty_fields()` is now returning instance id, instead of instance itself.


.. _v0.5:

0.5 (2015-05-06)
------------------

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
------------------

*New:*

    - Adding :code:`check_relationship` parameter on :code:`is_dirty` and :code:`get_dirty_field` methods to also check foreign key values.
