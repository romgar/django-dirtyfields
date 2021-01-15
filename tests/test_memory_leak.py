import gc
import resource

import pytest

from .models import ModelTest as DirtyMixinModel

pytestmark = pytest.mark.django_db


def test_rss_usage():
    DirtyMixinModel()
    gc.collect()
    rss_1 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    for _ in range(1000):
        DirtyMixinModel()
    gc.collect()
    rss_2 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    assert rss_2 == rss_1, 'There is a memory leak!'
