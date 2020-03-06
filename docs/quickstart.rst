Quickstart
==========

A simple example:

    >>> from querydict.parser import QueryEngine
    >>> john_1 = { "name": "John", "eye_colour": "Blue" }
    >>> john_2 = { "name": "John", "eye_colour": "Green" }
    >>> q = QueryEngine("name:Bob AND eye_colour:Blue")
    >>> q.match(john_1)
    True
    >>> q.match(john_2)
    False

.. _quickstart-queries:

Queries
-------
More complicated queries are possible, including nested dictionaries:

    >>> data = { "foo": { "bar": { "baz": { "wibble": "wobble" }}}}
    >>> q = QueryEngine("foo.bar.baz.wibble:wobble")
    >>> q.match(data)    # => True

And grouping inside the query:

    >>> england = { "country": "England", "continent": "Europe", "weather": "Rainy" }
    >>> spain = { "country": "Spain", "continent": "Europe", "weather": "Sunny" }
    >>> canada = { "country": "Canada", "continent": "North America", "weather": "Snowy"}
    >>> q = QueryEngine("(continent:Europe AND weather:Sunny) OR country:England")
    >>> q.match(england)    # => True
    True
    >>> q.match(spain)
    True
    >>> q.match(canada)
    False

.. _quickstart-ambiguous:

Ambiguous queries
-----------------
A query is considered ambiguous if the parser cannot determine how to combine different search terms.
This usually happens when multiple terms are included without specifying AND or OR, for example:

    >>> q = QueryEngine("state:Arizona weather:Wet")    # An ambiguous query, neither AND/OR is specified
    >>> q = QueryEngine("state:Arizona OR weather:Wet") # Well formed query, OR is given

The default behaviour is that AND will be used, ensuring all query terms need to match. This can be changed
to OR if required, or an exception can be forced (for example to validate queries and provide feedback to the user).

    >>> q = QueryEngine("state:Arizona weather:Wet", ambiguous_action="Exception")
    Traceback (most recent call last):
    ...
    querydict.parser.QueryException: Query contains an ambiguous (unknown) operation, use AND or OR