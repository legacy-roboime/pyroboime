#
# Copyright (C) 2013 RoboIME
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
"""
Utils for using with PyQt4
"""
from numpy import array
from numpy.linalg import norm
from PyQt4.QtGui import QPainterPath, QColor
from PyQt4.QtCore import Qt

from ..utils.mathutils import sin, cos, sqrt
SQRT2 = sqrt(2)


# colors
FIELD_GREEN = Qt.darkGreen
GREEN = Qt.green
BLUE = Qt.blue
YELLOW = Qt.yellow
RED = Qt.red
BLACK = Qt.black
WHITE = Qt.white
PINK = Qt.magenta
LIGHT_BLUE = Qt.cyan
LIGHT_GREY = QColor(0xcc, 0xcc, 0xcc)
ORANGE = QColor(0xff, 0xbb, 0x00)
TRANSPARENT = Qt.transparent


def scale(*meters):
    """to milimiters"""
    return (array(meters[0]) if len(meters) == 1 else array(meters)) * 1e3


def draw_arc(x, y, radius_in, radius_out, angle_init, angle_end, painter):
    path = QPainterPath()

    path.moveTo(x + radius_in * cos(angle_init), y + radius_in * sin(angle_init))
    path.arcTo(x - radius_out, y - radius_out, 2 * radius_out, 2 * radius_out, angle_init, angle_end - angle_init)
    path.arcTo(x - radius_in, y - radius_in, 2 * radius_in, 2 * radius_in, angle_end, angle_init - angle_end)
    path.closeSubpath()

    painter.drawPath(path)


def draw_x(painter, x, y, m):
    m = m / 2
    painter.drawLine(x - m, y - m, x + m, y + m)
    painter.drawLine(x - m, y + m, x + m, y - m)


def draw_arrow_line(painter, x0, y0, x1, y1, m):
    painter.drawLine(x0, y0, x1, y1)
    k = m * SQRT2 / norm(array([x1 - x0, y1 - y0])) / 2
    painter.drawLine(x1, y1, k * (x0 - x1 + y0 - y1) + x1 - x0, k * (x1 - x0 - y1 + y0) + y1 - y0)
    painter.drawLine(x1, y1, k * (x0 - x1 + y1 - y0) + x1 - x0, k * (x0 - x1 - y1 + y0) + y1 - y0)
