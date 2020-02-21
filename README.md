# lucene-dict-matcher - match Python dictionaries against Lucene queries

This library takes a Lucene syntax query and matches against Python dictionaries, returning `True` or `False`.
It is designed to allow selection of records that match user queries, for example in a streaming system where
data can be represented as a dictionary.
 
A simple example:

    from lucene_dict_matcher import QueryEngine
     
    john_1 = { "name": "John", "eye_colour": "Blue" }
    john_2 = { "name": "John", "eye_colour": "Green" }
    
    q = QueryEngine("name:Bob AND eye_colour:Blue")
    q.match(john_1)    # => True
    q.match(john_2)    # => False

More complicated queries are possible, including nested dictionaries:

    data = { "foo": { "bar": { "baz": { "wibble": "wobble" }}}}
    q = QueryEngine("foo.bar.baz.wibble:wobble")
    q.match(data)    # => True

And grouping inside the query:

    england = { "country": "England", "continent": "Europe", "weather": "Rainy" }
    spain = { "country": "Spain", "continent": "Europe", "weather": "Sunny" }
    
    q = QueryEngine("(continent:Europe AND weather:Sunny) OR country:England")
    q.match(england)    # => True
    q.match(spain)      # => True

# Installation

    pip install lucene-dict-matcher
    
Dependencies are automatically installed. Parsing of the Lucene query is handled by 
[luqum](https://github.com/jurismarches/luqum). Easy access to dictionary keys is
provided by [dotty-dict](https://pypi.org/project/dotty-dict/).