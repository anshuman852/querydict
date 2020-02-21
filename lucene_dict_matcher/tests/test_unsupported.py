"""
Test queries that aren't currently supported by this library, these are reminders
for new features to add.
"""
import pytest
from lucene_dict_matcher.parser import QueryEngine, QueryException

# TODO: Move into a common test module to avoid duplication
SIMPLE_DATA = {"key1": "value1", "key2": "value2"}


def test_range():
    with pytest.raises(QueryException):
        QueryEngine("price:[0 TO 10]")


def test_fuzzy():
    with pytest.raises(QueryException):
        QueryEngine("domain:microsoft~0.8")


def test_bare_field():
    with pytest.raises(NotImplementedError):
        QueryEngine("value1", allow_bare_field=True).match(SIMPLE_DATA, default_field="key1")