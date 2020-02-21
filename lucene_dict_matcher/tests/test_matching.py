import unittest
from lucene_dict_matcher import QueryEngine, QueryException


class TestMatching(unittest.TestCase):
    def setUp(self):
        self.simple_data = {"key1": "value1", "key2": "value2"}
        self.complex_data = {"country": "England", "data": {"weather": "Rainy"}}

    def test_missing(self):
        """ Test for a key that does not exist, ensuring it does not raise an exception. """
        q = QueryEngine("key3:value3")
        self.assertFalse(q.match(self.simple_data))

    def test_missing_nested(self):
        """ Test for a nested key that does not exist, ensuring it does not raise an exception. """
        q = QueryEngine("foo.bar.baz:missing")
        self.assertFalse(q.match(self.simple_data))

    def test_simple_and(self):
        q = QueryEngine("key1:value1 AND key2:value2")
        self.assertTrue(q.match(self.simple_data))

    def test_impossible_and(self):
        """ Test a condition that can never be true """
        q = QueryEngine("key1:value1 AND key1:value2")
        self.assertFalse(q.match(self.simple_data))

    def test_simple_or(self):
        q = QueryEngine("key1:value1 OR key2:value2")
        self.assertTrue(q.match(self.simple_data))

    def test_grouped_or(self):
        q = QueryEngine("country:France OR (country:England AND data.weather:Rainy)")
        self.assertTrue(q.match(self.complex_data))

    def test_nested(self):
        q = QueryEngine("country:England AND data.weather:Rainy")
        self.assertTrue(q.match(self.complex_data))

    def test_ambiguous_and(self):
        """ Ensure the default action for ambiguous queries is AND """
        q = QueryEngine("key1:value1 key2:value2")
        self.assertTrue(q.match(self.simple_data))


