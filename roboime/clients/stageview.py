from PyQt4.QtGui import QGraphicsItem, QGraphicsView, QColor, QBrush, QPainter, QGraphicsScene
from PyQt4.QtCore import QRectF, Qt
#from ..utils.mathutils import sin, cos

# some known uuids
BALL = 0xba11
FIELD = 0xf1e1d

# colors
GREEN = Qt.green
BLUE = Qt.blue
YELLOW = Qt.yellow
BLACK = Qt.black
WHITE = Qt.white
ORANGE = QColor(0xff, 0xbb, 0x00)

# some settings
BORDER = 10


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
            return GREEN
        elif self.robot.is_blue:
            return BLUE
        elif self.robot.is_blue:
            return YELLOW
        else:
            return BLACK

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

    def __init__(self, world):
        super(FieldItem, self).__init__()
        self.world = world

    @property
    def uuid(self):
        return FIELD

    def boundingRect(self):
        w = self.world
        return QRectF(-w.length / 2, -w.width / 2, w.length, w.width)

    def paint(self, painter, option, widget):
        painter.setPen(WHITE)

        painter.drawRect(self.boundingRect())


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
        painter.setBrush(ORANGE)
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
        scene = self.scene()
        scene.clear()
        with self.world as w:
            field = FieldItem(w)
            scene.addItem(field)
            field.setPos(-w.length / 2, -w.width / 2)

            #self.setScene(QGraphicsScene(-w.width / 2, -w.length / 2, w.width, w.length))
            #scene = self.scene()

            #uuids = []
            #for item in scene.items():
            #    uuids.append(item.uuid)

            #if BALL not in uuids:
            #    print 'Adding ball to scene:', uuids
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

            self.fitInView(-w.length / 2 - BORDER, -w.width / 2 - BORDER, w.width + 2 * BORDER, w.length + 2 * BORDER, Qt.KeepAspectRatio)
