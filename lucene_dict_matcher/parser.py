from dotty_dict import dotty
from luqum.parser import parser, ParseError
from luqum.tree import (
    AndOperation,
    OrOperation,
    Group,
    SearchField,
    Word,
    Phrase,
    Fuzzy,
    UnknownOperation,
    Range,
)
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

    def __init__(
        self,
        query,
        short_circuit=True,
        ambiguous_action="AND",
        allow_bare_field=False,
        max_depth=10,
    ):
        """

        """

        if ambiguous_action not in self.ambiguous_actions:
            raise ValueError(
                "Invalid ambiguous_action, expected one of AND, OR, Exception"
            )

        self.short_circuit = short_circuit
        self.allow_bare_field = allow_bare_field
        self.max_depth = max_depth
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
            raise QueryException(
                "Could not parse the query, error: {}".format(str(exc))
            )

        # Replace any UnknownOperation with the chosen action
        if ambiguous_action != "Exception":
            operation = self.ambiguous_actions[ambiguous_action]
            resolver = UnknownOperationResolver(resolve_to=operation)
            self._tree = resolver(self._tree)

        # Raise a QueryException if the user has passed unsupported search terms
        self._check_tree(self._tree)

    def _check_tree(self, root, parent=None, depth=0):
        """ Check for unsupported object types in the tree """

        depth += 1
        if depth > self.max_depth:
            raise QueryException(
                "Query too complicated, increase max_depth if required"
            )

        # Check for Word/Phrase objects that don't have SearchField as a parent. If configured to
        # allow this, flag at the object level so match() can require a default field.
        if any(isinstance(root, t) for t in [Word, Phrase]) and not isinstance(
            parent, SearchField
        ):
            if not self.allow_bare_field:
                raise QueryException("Query contains search term without a named field")

            self._contains_bare_field = True

        elif isinstance(root, UnknownOperation):
            raise QueryException(
                "Query contains an ambiguous (unknown) operation, use AND or OR"
            )

        elif isinstance(root, Fuzzy):
            # TODO: Implement with levenshtein matching
            raise QueryException("Fuzzy matching with ~ is not currently supported")

        elif isinstance(root, Range):
            # TODO: Implement, noting difference between [] (inclusive) and {} (exclusive)
            raise QueryException(
                "Range matching with [..] or {..} is not currently supported"
            )

        elif not any(isinstance(root, t) for t in self.supported_ops):   # pragma: no cover
            raise QueryException(
                "Unsupported operation type {}, please file a bug".format(str(root))
            )

        for child in root.children:
            self._check_tree(child, root, depth)

    def match(self, data, default_field=None):
        if self._contains_bare_field and default_field is None:
            raise MatchException(
                "Need a default_field to use for matching unqualified field"
            )

        data = dotty(data)
        return self._match(data, self._tree)

    def _match(self, data, operation):

        op_map = {
            SearchField: self._search_field,
            AndOperation: self._and,
            OrOperation: self._or,
            Group: self._group,
            Word: self._bare_field,
            Phrase: self._bare_field,
        }

        handler_fn = op_map.get(type(operation), None)

        if handler_fn is None:   # pragma: no cover
            raise Exception("Unhandled operation type {}".format(str(type(operation))))

        result = handler_fn(data, operation)
        return result

    def _group(self, data, operation):
        """
        This simply strips the Group object and passes the first child back to match.
        """
        if len(operation.children) > 1:   # pragma: no cover
            raise Exception(
                "Unhandled Group with more than 1 child, please report a bug"
            )

        return self._match(data, operation.children[0])

    def _and(self, data, operation):
        result = True

        for child in operation.children:
            if not self._match(data, child):
                # Failure of one AND component means none can match, return immediately
                if self.short_circuit:
                    return False

                result = False

        return result

    def _or(self, data, operation):
        result = False

        for child in operation.children:
            if self._match(data, child):
                # Success of one OR component means it's a match
                if self.short_circuit:
                    return True

                result = True

        return result

    def _bare_field(self, data, operation):
        """
        Process a
        """
        raise NotImplementedError("Unimplemented")

    def _search_field(self, data, operation):
        """
        Process a single SearchField object, which should have either a Word() or Phrase()
        as a child.  Fuzzy() and Range() are not currently supported.
        """

        if len(operation.children) > 1:   # pragma: no cover
            raise Exception(
                "Unhandled SearchField with more than 1 child, please report a bug"
            )

        # logging.debug("Checking field %s against condition %s", op.name, op.expr)

        try:
            field = data[operation.name]
        except KeyError:
            # logging.debug("Field %s was not found in the input data", op.name)
            return False

        match = operation.children[0]

        # TODO: Check data type, e.g. for an int field we expect integer in the search query

        if isinstance(match, Word):
            return field == match.value

        if isinstance(match, Phrase):
            # Strip the quotes, first check these are always here
            if match.value[0] != '"' or match.value[-1] != '"':   # pragma: no cover
                raise Exception(
                    "Expected Phrase to start and end with double quotes, please report a bug"
                )

            return match.value[1:-1] in field
