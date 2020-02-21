import unittest
from lucene_dict_matcher import QueryEngine, QueryException


class TestUnsupportedOperations(unittest.TestCase):
    """ Queries that aren't currently supported by this library, reminders for features to add """

    def test_range(self):
        with self.assertRaises(QueryException):
            q = QueryEngine("price:[0 TO 10]")

    def test_fuzzy(self):
        with self.assertRaises(QueryException):
            q = QueryEngine("domain:microsoft~0.8")