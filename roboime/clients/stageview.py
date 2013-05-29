from PyQt4.QtGui import QGraphicsItem, QGraphicsView, QColor, QBrush, QPainter, QGraphicsScene
from PyQt4.QtCore import QRectF, Qt
from ..base import Blue, Yellow
from ..utils.mathutils import sin, cos

import pdb

class RobotItem(QGraphicsItem):
    def __init__(self, radius, angle, teamColor, parent=None, scene=None):
        super(RobotItem, self).__init__()
        self.angle = angle
        self.radius = 10*radius
        self._color = teamColor

    @property
    def color(self):
        #if self.isSelected(): 
        #    return Qt.green
        if self._color == Blue:
            return Qt.blue
        else:
            return Qt.yellow

    def boundingRect(self):
        return QRectF(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)

    def paint(self, painter, option, widget=None):
        #print 'oaaonadoasndoaskdiaasnjido'
        #print painter
        painter.setBrush(self.color)
        painter.drawEllipse(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)
        #painter.drawLine(0, 0, self.radius * cos(self.angle), self.radius * sin(self.angle))
        #painter.drawText(0, 0, "Teste")


class FieldItem(QGraphicsItem):
    pass


class BallItem(QGraphicsItem):
    pass


class StageView(QGraphicsView):
    def __init__(self, parent=None):
        super(StageView, self).__init__(parent)
        self.setBackgroundBrush(QBrush(Qt.darkGreen))
        self.setCacheMode(QGraphicsView.CacheNone)
        self.setRenderHints(QPainter.Antialiasing)
        self.setRenderHints(QPainter.SmoothPixmapTransform)
        self.setScene(QGraphicsScene(0, 0, 0, 0))

    def redraw(self):
        w = self.world
        self.scene().clear()
        self.setScene(QGraphicsScene(-w.width/2, -w.length/2, w.width, w.length))
        for r in w.iterrobots():
            #from PyQt4.QtCore import pyqtRemoveInputHook
            #from pdb import set_trace
            #pyqtRemoveInputHook()
            #set_trace()
            #print r.radius, r.angle, r.color, r.x, r.y
            ri = RobotItem(r.radius, r.angle, r.color)
            #print ri.radius, ri.angle, ri.color
            self.scene().addItem(ri)
            print r.x, r.y, w.width, w.length
            ri.setPos(r.x, r.y)
        BORDER = 0.5
        self.fitInView(-w.length / 2 - 5 * BORDER, -w.width / 2 - 5 * BORDER, w.length + 10 * BORDER, w.width+ 10 * BORDER, Qt.KeepAspectRatio)
