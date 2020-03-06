"""
Tests for the query parsing engine, ensuring that valid and invalid queries are handled appropriately.
"""
import pytest
from querydict.parser import QueryEngine, QueryException


def test_none():
    """ Test that passing None raises a ValueError """
    with pytest.raises(ValueError):
        QueryEngine(None)


def test_empty():
    """ Test that empty queries, including whitespace, raise a ValueError """
    with pytest.raises(ValueError):
        QueryEngine("")

    with pytest.raises(ValueError):
        QueryEngine("    ")


def test_invalid_args():
    """ An invalid action to take when statement without AND/OR is found """
    with pytest.raises(ValueError):
        QueryEngine("foo bar", ambiguous_action="DANCE")


def test_invalid_query():
    """ An invalid query string that luqum will not parse """
    with pytest.raises(QueryException):
        QueryEngine("foo(:bar)")


def test_max_depth():
    """ Query that generates an AST requiring too much recursion """
    with pytest.raises(QueryException):
        QueryEngine("((foo:bar) AND ((bar:baz) OR (baz:foo)))", max_depth=2)


def test_basic():
    """ Test a very basic query with a Word in a single field """
    QueryEngine("key:value")


def test_ambiguous():
    """ Test queries that lack AND/OR so are ambiguous """

    # This should work, the default action is to replace with AND
    QueryEngine("key:value oops:ambiguous")

    with pytest.raises(QueryException):
        QueryEngine("key:value oops:ambiguous", ambiguous_action="Exception")


def test_bare_field():
    """ Test that values without a field name are handled correctly """
    QueryEngine("value", allow_bare_field=True)

    with pytest.raises(QueryException):
        QueryEngine("value", allow_bare_field=False)
