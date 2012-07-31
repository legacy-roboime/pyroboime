"""Geometry classes."""
from shapely import geometry

class Point(geometry.Point):
    pass

class Circle(Point):
    pass

class Line(geometry.LineString):
    pass

