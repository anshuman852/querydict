"""
Test queries that aren't currently supported by this library, these are reminders
for new features to add.
"""
import pytest
from querydict.parser import QueryEngine, QueryException

# TODO: Move into a common test module to avoid duplication
SIMPLE_DATA = {"key1": "value1", "key2": "value2"}


def test_range():
    """ Test queries that generate a Range() object """
    with pytest.raises(QueryException):
        QueryEngine("price:[0 TO 10]")


def test_fuzzy():
    """ Test queries that include a fuzzy (Levenshtein) match """
    with pytest.raises(QueryException):
        QueryEngine("domain:microsoft~0.8")


def test_bare_field():
    """ Test that passing a value with no fieldname raises NotImplementedError during matching """
    with pytest.raises(NotImplementedError):
        QueryEngine("value1", allow_bare_field=True).match(
            SIMPLE_DATA, default_field="key1"
        )
