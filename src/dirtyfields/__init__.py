"""
django-dirtyfields library for tracking dirty fields on a Model instance.

Adapted from https://stackoverflow.com/questions/110803/dirty-fields-in-django
"""

__all__ = ['DirtyFieldsMixin']
__version__ = "1.8.3.dev0"

from dirtyfields.dirtyfields import DefaultDirtyFieldsMixin, DirtyFieldsMixin

VERSION = tuple(map(int, __version__.split(".")[0:3]))
