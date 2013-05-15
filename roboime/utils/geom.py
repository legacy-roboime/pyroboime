"""Geometry classes."""
from shapely import geometry


class Point(geometry.Point):
    pass


class Circle(geometry.Polygon):

    def __init__(self, center, radius):
        """
        A circle of radius 2.0, centered on (1.0, 0.0):
        >>> p = Point(1.0, 0.0)
        >>> c = Circle(p, 2.0)

        The circle is a shapely polygon
        >>> len(c.exterior.coords)
        66
        """
        # the following is not really optimized as it creates a polygon twice
        # but it's ok for now, I tried doing some magic with __new__, didn't work
        super(Circle, self).__init__(center.buffer(radius).exterior.coords)
        self._center = center
        self._radius = radius

    @property
    def center(self):
        return self._center

    @property
    def radius(self):
        return self._radius


class Line(geometry.LineString):
    pass
