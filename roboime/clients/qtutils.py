"""
Utils for using with PyQt4
"""
from numpy import array
from PyQt4.QtGui import QPainterPath, QColor
from PyQt4.QtCore import Qt

from ..utils.mathutils import sin, cos


# colors
FIELD_GREEN = Qt.darkGreen
GREEN = Qt.green
BLUE = Qt.blue
YELLOW = Qt.yellow
RED = Qt.red
BLACK = Qt.black
WHITE = Qt.white
LIGHT_GREY = QColor(0xcc, 0xcc, 0xcc)
ORANGE = QColor(0xff, 0xbb, 0x00)


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
