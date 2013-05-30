"""
Utils for using with PyQt4
"""
from numpy import array


def scale(*meters):
    """to milimiters"""
    return (array(meters[0]) if len(meters) == 1 else array(meters)) * 1e3
