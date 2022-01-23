Contributing
============
If you're interested in developing the project, the unit tests can be run locally using ``tox``:

.. code-block:: bash

    $ pip install tox
    $ tox -e py310-django32-sqlite

If you want to run the tests against PostgreSQL you will need to set the POSTGRES_USER and POSTGRES_PASSWORD
environment variables:

.. code-block:: bash

    $ export POSTGRES_USER=user
    $ export POSTGRES_PASSWORD=password
    $ tox -e py310-django32-postgresql

You can also run the entire test matrix (WARNING: this will run the test suite a large number of times):

.. code-block:: bash

    $ tox -e ALL
