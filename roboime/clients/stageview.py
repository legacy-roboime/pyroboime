from PyQt4.QtGui import QGraphicsItem, QGraphicsView, QColor, QBrush, QPainter, QGraphicsScene
from PyQt4.QtCore import QRectF, Qt
from ..utils.mathutils import sin, cos


BALL = 0xba11
FIELD = 0xf1e1d


class RobotItem(QGraphicsItem):
    def __init__(self, robot):
        super(RobotItem, self).__init__()
        self.robot = robot

    @property
    def uuid(self):
        return self.robot.uuid

    @property
    def color(self):
        if self.isSelected():
            return Qt.green
        elif self.robot.is_blue:
            return Qt.blue
        elif self.robot.is_blue:
            return Qt.yellow
        else:
            return Qt.black

    @property
    def radius(self):
        return self.robot.radius

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

    @property
    def uuid(self):
        return FIELD


class BallItem(QGraphicsItem):

    def __init__(self, ball):
        super(BallItem, self).__init__()
        self.ball = ball

    @property
    def radius(self):
        return self.ball.radius

    @property
    def uuid(self):
        return BALL

    def boundingRect(self):
        return QRectF(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)

    def paint(self, painter, option, widget=None):
        painter.setBrush(Qt.yellow)
        painter.drawEllipse(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)
        #painter.drawLine(0, 0, self.radius * cos(self.angle), self.radius * sin(self.angle))
        #painter.drawText(0, 0, "Teste")


class StageView(QGraphicsView):
    def __init__(self, parent=None):
        super(StageView, self).__init__(parent)
        self.setBackgroundBrush(QBrush(Qt.darkGreen))
        self.setCacheMode(QGraphicsView.CacheNone)
        self.setRenderHints(QPainter.Antialiasing)
        self.setRenderHints(QPainter.SmoothPixmapTransform)
        self.setScene(QGraphicsScene(0, 0, 0, 0))

    def redraw(self):
        with self.world as w:
            pass
            #self.setScene(QGraphicsScene(-w.width / 2, -w.length / 2, w.width, w.length))
            #scene = self.scene()

            #uuids = []
            #for item in scene.items():
            #    uuids.append(item.uuid)

            #if BALL not in uuids:
            #    scene.addItem(BallItem(w.ball))

            #for r in w.iterrobots():
            #    #from PyQt4.QtCore import pyqtRemoveInputHook
            #    #from pdb import set_trace
            #    #pyqtRemoveInputHook()
            #    #set_trace()
            #    #print r.radius, r.angle, r.color, r.x, r.y
            #    ri = RobotItem(r.radius, r.angle, r.is_blue)
            #    self.scene().addItem(ri)
            #    ri.setPos(r.x, r.y)
