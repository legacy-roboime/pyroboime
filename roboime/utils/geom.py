"""Geometry classes."""
from shapely import geometry


class Point(geometry.Point):
    pass


class Circle(Point):

    def __init__(self, radius=1.0, *args, **kwargs):
        """
        A circle of radius 2.0, centered on (1.0, 0.0):
        >>> c = Circle(2.0, 1.0, 0.0)

        The shape of the circle is the actual shapely polygon:
        >>> len(c.shape.exterior.coords)
        66
        """
        super(Circle, self).__init__(*args, **kwargs)
        self._radius = radius

    @property
    def shape(self):
        return self.buffer(self._radius)

    @property
    def radius(self):
        return self._radius


class Line(geometry.LineString):
    pass
