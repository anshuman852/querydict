import unittest
from lucene_dict_matcher import QueryEngine, QueryException


class TestQueryParsing(unittest.TestCase):

    def test_none(self):
        with self.assertRaises(ValueError):
            q = QueryEngine(None)

    def test_empty(self):
        with self.assertRaises(ValueError):
            q = QueryEngine("")

        with self.assertRaises(ValueError):
            q = QueryEngine("    ")

    def test_basic(self):
        q = QueryEngine("key:value")

    def test_ambiguous(self):
        # This should work, the default action is to replace with AND
        q = QueryEngine("key:value oops:ambiguous")

        with self.assertRaises(QueryException):
            q = QueryEngine("key:value oops:ambiguous", ambiguous_action="Exception")

    def test_bare_field(self):
        q = QueryEngine("value", allow_bare_field=True)

        with self.assertRaises(QueryException):
            q = QueryEngine("value", allow_bare_field=False)