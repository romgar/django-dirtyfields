import django
import unittest


def get_model_name(klass):
    if hasattr(klass._meta, 'model_name'):
        model_name = klass._meta.model_name
    else:  # Django < 1.6
        model_name = klass._meta.module_name

    return model_name


def skip_before_django_15(test):
    if django.VERSION < (1, 5):
        return unittest.skip('save dirty fields is not different that basic save() before django 1.5')(test)
    return test
