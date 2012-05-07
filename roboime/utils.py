"""
Some utils.
"""
from numpy import ndarray, isnan


class Particle(ndarray):
    """Every object that has a position subclasses this class."""
    
    def __new__(cls, *args, **kwargs):
        self = ndarray.__new__(cls, shape=(3))
        self[0] = self[1] = self[2] = None
        return self

    @property
    def x(self):
        return self[0] if not isnan(self[0]) else None

    @x.setter
    def x(self, value):
        self[0] = value

    @property
    def y(self):
        return self[1] if not isnan(self[1]) else None

    @y.setter
    def y(self, value):
        self[1] = value

    @property
    def z(self):
        return self[2] if not isnan(self[2]) else None

    @z.setter
    def z(self, value):
        self[2] = value
