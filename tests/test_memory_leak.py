import resource

import pytest

from .models import TestModel as DirtyMixinModel

pytestmark = pytest.mark.django_db


def test_rss_usage():
    DirtyMixinModel()
    rss_1 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    for _ in range(1000):
        DirtyMixinModel()
    rss_2 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    diff_percentage = 100 * abs(rss_2 - rss_1) / rss_1
    assert diff_percentage <= 1, 'There is a memory leak!'
