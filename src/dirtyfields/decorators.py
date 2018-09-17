import functools
from .exceptions import DirtyFieldsDisabled


def require_non_disabled(func):
    """Decorator to use on methods that should not be used when dirtyfields
    is disabled. It will raise an error when that happens.

    """

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._dirtyfields_disabled:
            # Get the bound method from the current object to get better log information
            func_log = getattr(self, func.__name__)
            raise DirtyFieldsDisabled(
                f'Dirtyfields is disabled and is being used: unsafe operation - {func_log}'
            )

        return func(self, *args, **kwargs)

    return wrapper
