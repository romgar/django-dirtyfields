import datetime
import pytz
import warnings

from django.conf import settings
from django.utils import timezone


def raw_compare(cls, new_value, old_value):
    return new_value != old_value


def time_zone_support_compare(cls, new_value, old_value):

    if isinstance(new_value, datetime.datetime) and isinstance(old_value, datetime.datetime):
        db_value_is_aware = timezone.is_aware(old_value)
        in_memory_value_is_aware = timezone.is_aware(new_value)

        if db_value_is_aware != in_memory_value_is_aware:
            if settings.USE_TZ:
                # It USE_TZ is True, db value is aware, so we need to convert in-memory one
                # The logic here is the one applied in django.db.models.fields.DateTimeField.to_python
                warnings.warn(u"DateTimeField received a naive datetime (%s)"
                              u" while time zone support is active." % new_value,
                              RuntimeWarning)
                default_timezone = timezone.get_default_timezone()
                new_value = timezone.make_aware(new_value, default_timezone)
            else:
                # The db is not timezone aware, but the value we are passing for comparison is aware.
                # By default, we then compare to UTC.
                warnings.warn(u"Time zone support is not active, and you pass a time zone aware value (%s)"
                              u" Converting database value to UTC before comparison." % new_value,
                              RuntimeWarning)
                old_value = timezone.make_aware(old_value, pytz.UTC)

    return new_value != old_value
