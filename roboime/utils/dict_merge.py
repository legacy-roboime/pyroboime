"""
Don't know why this is a module...
"""
from copy import deepcopy


def dict_merge(a, b):
    """
    Recursively merges dict's. not just simple a['key'] = b['key'], if
    both a and bhave a key who's value is a dict then dict_merge is called
    on both values and the result stored in the returned dictionary.

    Borrowed from: http://www.xormedia.com/recursively-merge-dictionaries-in-python/
    The typical use case is merging local and default configurations.

    Example:
    >>> a = {'a': {'b': 4, 'c': 5}, 'd': 6}
    >>> b = {'a': {'c': 99, 'd': 0}, 'e': 'abcd'}
    >>> dict_merge(a, b)
    {'a': {'b': 4, 'c': 99, 'd': 0}, 'd': 6, 'e': 'abcd'}
    """

    return _dict_merge(a, b) or {}


def _dict_merge(a, b):
    if not isinstance(b, dict):
        return b
    result = deepcopy(a)

    for k, v in b.items():
        if k in result and isinstance(result[k], dict):
                result[k] = _dict_merge(result[k], v)
        else:
            result[k] = deepcopy(v)

    return result
