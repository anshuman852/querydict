import logging
from dotty_dict import dotty
from luqum.parser import parser, ParseError
from luqum.tree import *
from luqum.utils import UnknownOperationResolver


class QueryException(Exception):
    pass


class MatchException(Exception):
    pass


class QueryEngine:
    """
    Match a Lucene query against dict data, using an abstract tree parser.
    """

    supported_ops = [AndOperation, OrOperation, Group, SearchField, Word, Phrase]
    ambiguous_actions = {"Exception": None, "AND": AndOperation, "OR": OrOperation}

    def __init__(self, query, short_circuit=True, ambiguous_action="AND", allow_bare_field=False):
        """

        """

        if ambiguous_action not in self.ambiguous_actions:
            raise ValueError(
                "Invalid ambiguous_action, expected one of AND, OR, Exception"
            )

        self.short_circuit = short_circuit
        self.allow_bare_field = allow_bare_field
        self._contains_bare_field = False
        self._parse_query(query, ambiguous_action)

    def _parse_query(self, query, ambiguous_action):
        """
        Parse the query, replace any ambiguous (unknown) parts with the correct operation
        and check for unsupported operations.
        """
        if query is None or query.strip() == "":
            raise ValueError("Need a valid query")

        try:
            self._tree = parser.parse(query)
        except ParseError as exc:
            raise QueryException("Could not parse the query, error: %s", str(exc))

        # Replace any UnknownOperation with the chosen action
        if ambiguous_action != "Exception":
            operation = self.ambiguous_actions[ambiguous_action]
            resolver = UnknownOperationResolver(resolve_to=operation)
            self._tree = resolver(self._tree)

        # Raise a QueryException if the user has passed unsupported search terms
        self._check_tree(self._tree)

    def _check_tree(self, root, parent=None):
        """ Check for unsupported object types in the tree """

        # Check for Word/Phrase objects that don't have SearchField as a parent. If configured to
        # allow this, flag at the object level so match() can require a default field.
        if type(root) in [Word, Phrase] and type(parent) != SearchField:
            if not self.allow_bare_field:
                raise QueryException("Query contains search term without a named field")
            else:
                self._contains_bare_field = True

        elif type(root) == UnknownOperation:
            raise QueryException(
                "Query contains an ambiguous (unknown) operation, use AND or OR"
            )

        elif type(root) == Fuzzy:
            # TODO: Implement with levenshtein matching
            raise QueryException("Fuzzy matching with ~ is not currently supported")

        elif type(root) == Range:
            # TODO: Implement, paying attention to the difference between [] (inclusive) and {} (exclusive)
            raise QueryException(
                "Range matching with [..] or {..} is not currently supported"
            )

        elif type(root) not in self.supported_ops:
            raise QueryException(
                "Unsupported operation type %s, please file a bug", str(root)
            )

        for child in root.children:
            self._check_tree(child, root)

    def match(self, data, default_field=None):
        if self._contains_bare_field and default_field is None:
            raise MatchException("Need a default_field to use for matching unqualified field")

        data = dotty(data)
        return self._match(data, self._tree)

    def _match(self, data, op):

        op_map = {
            SearchField: self._search_field,
            AndOperation: self._and,
            OrOperation: self._or,
            Group: self._group,
        }

        # TODO: Consider resource exhaustion
        # TODO: Make it possible to call this to validate the query, e.g. by passing data as a dict that always returns keys

        handler_fn = op_map.get(type(op), None)

        if handler_fn is None:
            raise Exception("Unhandled operation type %s", str(type(op)))

        result = handler_fn(data, op)
        return result

    def _group(self, data, op):
        """
        This simply strips the Group object and passes the first child back to match.
        """
        if len(op.children) > 1:
            raise Exception(
                "Unhandled Group with more than 1 child, please report a bug"
            )

        return self._match(data, op.children[0])

    def _and(self, data, op):
        result = True

        for child in op.children:
            if not self._match(data, child):
                # Failure of one AND component means none can match, return immediately
                if self.short_circuit:
                    return False

                result = False

        return result

    def _or(self, data, op):
        result = False

        for child in op.children:
            if self._match(data, child):
                # Success of one OR component means it's a match
                if self.short_circuit:
                    return True

                result = True

        return result

    def _bare_field(self, data, op):
        """
        Process a
        """
        raise Exception("Unimplemented")

    def _search_field(self, data, op):
        """
        Process a single SearchField object, which should have either a Word() or Phrase()
        as a child.  Fuzzy() and Range() are not currently supported.
        """

        if len(op.children) > 1:
            raise Exception(
                "Unhandled SearchField with more than 1 child, please report a bug"
            )

        # logging.debug("Checking field %s against condition %s", op.name, op.expr)

        try:
            field = data[op.name]
        except KeyError:
            # logging.debug("Field %s was not found in the input data", op.name)
            return False

        match = op.children[0]

        # TODO: Check type of the data, e.g. for an integer input field we expect integer in the search query

        if type(match) == Word:
            return field == match.value

        elif type(match) == Phrase:
            # Strip the quotes, first check these are always here
            if match.value[0] != '"' or match.value[-1] != '"':
                raise Exception(
                    "Expected Phrase object to start and end with double quotes, please report a bug"
                )

            return match.value[1:-1] in field

        else:
            raise Exception(
                "Unhandled match type %s, please report a bug", str(type(match))
            )
