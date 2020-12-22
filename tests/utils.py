import re

from django.conf import settings
from django.db import connection


class assert_number_queries(object):

    def __init__(self, number):
        self.number = number

    def matched_queries(self):
        return connection.queries

    def query_count(self):
        return len(self.matched_queries())

    def __enter__(self):
        self.DEBUG = settings.DEBUG
        settings.DEBUG = True
        self.num_queries_before = self.query_count()

    def __exit__(self, type, value, traceback):
        self.num_queries_after = self.query_count()
        assert self.num_queries_after - self.num_queries_before == self.number
        settings.DEBUG = self.DEBUG


class RegexMixin(object):
    regex = None

    def matched_queries(self):
        matched_queries = super(RegexMixin, self).matched_queries()

        if self.regex is not None:
            pattern = re.compile(self.regex)
            regex_compliant_queries = [query for query in matched_queries if pattern.match(query.get('sql'))]

        return regex_compliant_queries


class assert_number_of_queries_on_regex(RegexMixin, assert_number_queries):

    def __init__(self, regex, number):
        super(assert_number_of_queries_on_regex, self).__init__(number)
        self.regex = regex


class assert_select_number_queries_on_model(assert_number_of_queries_on_regex):

    def __init__(self, model_class, number):
        model_name = model_class._meta.model_name
        regex = r'^.*SELECT.*FROM "tests_%s".*$' % model_name

        super(assert_select_number_queries_on_model, self).__init__(regex, number)


def is_postgresql_env_with_jsonb_field():
    try:
        PG_VERSION = connection.pg_version
    except AttributeError:
        PG_VERSION = 0

    return PG_VERSION >= 90400
