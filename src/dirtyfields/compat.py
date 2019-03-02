import sys


def is_buffer(value):
    if sys.version_info < (3, 0, 0):
        return isinstance(value, buffer)  # noqa
    else:
        return isinstance(value, memoryview)
