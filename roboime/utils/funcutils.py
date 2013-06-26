

def chained(*args):
    """
    This function will return a function that is a chain of the given functions.

    That is, for instance:

    >>> def a():
    ...     print 'A!'
    ...
    >>> def b():
    ...     print 'B!'
    ...
    >>> a()
    A!
    >>> b()
    B!
    >>> c = chained(a, b)
    >>>
    >>> c()
    A!
    B!
    [None, None]
    """
    return lambda: map(lambda x: x(), args)
