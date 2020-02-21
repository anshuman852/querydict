"""
Match Python dictionaries
"""
from .parser import QueryEngine, QueryException, MatchException

VERSION_MAJOR = 0
VERSION_MINOR = 0
VERSION_PATCH = 1
VERSION_STRING = ".".join(str(i) for i in [VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH])
