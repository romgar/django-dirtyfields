ChangeLog
=========

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
