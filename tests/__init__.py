import os
import django

# Needed for django tests
os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.django_settings'
if django.VERSION >= (1, 7, 0):
    # setup() call is needed for django 1.7+
    django.setup()
