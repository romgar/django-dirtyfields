import re

from django.conf import settings
from django.db import connection


class assert_number_queries(object):

    def __init__(self, number):
        self.number = number

    def query_count(self):
        return len(connection.queries)

    def __enter__(self):
        self.DEBUG = settings.DEBUG
        settings.DEBUG = True
        self.num_queries_before = self.query_count()

    def __exit__(self, type, value, traceback):
        self.num_queries_after = self.query_count()
        assert self.num_queries_after - self.num_queries_before == self.number
        settings.DEBUG = self.DEBUG


class assert_select_number_queries_on_model(assert_number_queries):

    def __init__(self, model_class, number):
        super(assert_select_number_queries_on_model, self).__init__(number)
        self.model_class = model_class

    def query_count(self):

        if hasattr(self.model_class._meta, 'model_name'):
            model_name = self.model_class._meta.model_name
        else:  # < 1.6
            model_name = self.model_class._meta.module_name

        pattern = re.compile(r'^.*SELECT.*FROM "tests_%s".*$' % model_name)
        cnt = len([query for query in connection.queries if pattern.match(query.get('sql'))])

        return cnt
