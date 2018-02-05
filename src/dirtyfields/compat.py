from distutils.version import StrictVersion
import sys
import django


PY3 = sys.version_info[0] == 3


def get_m2m_with_model(given_model):
    if StrictVersion(django.get_version()) < StrictVersion('1.9'):
        return given_model._meta.get_m2m_with_model()
    else:
        return [
            (f, f.model if f.model != given_model else None)
            for f in given_model._meta.get_fields()
            if f.many_to_many and not f.auto_created
        ]


def is_buffer(value):
    if PY3:
        buffer_type = memoryview
    else:
        buffer_type = buffer  # noqa
    return isinstance(value, buffer_type)


def remote_field(field):
    if StrictVersion(django.get_version()) < StrictVersion('1.9'):
        return field.rel
    else:
        return field.remote_field
