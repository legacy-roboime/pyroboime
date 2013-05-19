"""Geometry classes."""
from shapely import geometry
from numpy import cross
from numpy.linalg import norm


class Point(geometry.Point):
    def distance_to_line(self, line):
        """ Distance to a line, NOT a segment."""
        x0, y0 = line.coords[0]
        x1, y1 = line.coords[1]
        return norm(cross([self.x - x0, self.y - y0, 0.0], [x1 - x0, y1 - y0, 0.0]))
    
    def update(self, *args, **kwargs):
        """ This reconstructs the current point with a new set of coordinates so that
        we can work around the fact that shapely points cannot have their coordinate sets changed
        """
        super(Point, self).__init__(*args, **kwargs)

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
    def __init__(self, *args, **kwargs):
        """If you're passing anything aside from the coordinates, please use kwargs."""
        if len(args) > 1:
            x1, y1, x2, y2 = args[0].x, args[0].y, args[1].x, args[1].y
            super(Line, self).__init__([(x1, y1), (x2, y2)], **kwargs)
        else:
            super(Line, self).__init__(*args, **kwargs)

    def normal_vector(self):
        """Will return a numpy array with two coordinates that is normal to the line."""
        x1, y1 = self.coords[0]
        x2, y2 = self.coords[1]
        v = cross((x1 - x2, y1 - y2, 0.0), (0.0, 0.0, 1.0))[:2]
        return v / norm(v)
