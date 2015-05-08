#!/usr/bin/env python
import os
import sys
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
# These imports have to be done after DJANGO_SETTINGS_MODULE setting (needed for Django 1.4/1.5/1.6)
from django.conf import settings
from django.test.utils import get_runner


if __name__ == "__main__":
    try:
        django.setup()
    except AttributeError:
        # setup() call is needed for django 1.7+
        pass
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["tests"])
    sys.exit(bool(failures))
