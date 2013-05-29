from numpy import array
from PyQt4.QtGui import QGraphicsItem, QGraphicsView, QColor, QBrush, QPainter, QGraphicsScene, QPainterPath
from PyQt4.QtCore import QRectF, Qt

from ..utils.mathutils import sin, cos

# some known uuids
BALL = 0xba11
FIELD = 0xf1e1d

# colors
FIELD_GREEN = Qt.darkGreen
GREEN = Qt.green
BLUE = Qt.blue
YELLOW = Qt.yellow
BLACK = Qt.black
WHITE = Qt.white
ORANGE = QColor(0xff, 0xbb, 0x00)

# some settings
BORDER = 200.0


def scale(*meters):
    """to milimiters"""
    #return (meters * 1e3) if len(meters) == 1 else tuple(m * 1e3 for m in meters)
    return array(meters) * 1e3
s = scale


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


def draw_arc(x, y, radius_in, radius_out, angle_init, angle_end, painter):
    path = QPainterPath()

    path.moveTo(x + radius_in * cos(angle_init), y + radius_in * sin(angle_init))
    path.arcTo(x - radius_out, y - radius_out, 2 * radius_out, 2 * radius_out, angle_init, angle_end - angle_init)
    path.arcTo(x - radius_in, y - radius_in, 2 * radius_in, 2 * radius_in, angle_end, angle_init - angle_end)
    path.closeSubpath()

    painter.drawPath(path)


class FieldItem(QGraphicsItem):

    def __init__(self, world):
        super(FieldItem, self).__init__()
        self.world = world

    @property
    def uuid(self):
        return FIELD

    def boundingRect(self):
        width, height = s(self.world.length), s(self.world.width)
        return QRectF(-1.5 * width, -1.5 * height, 3 * width, 3 * height);

    def paint(self, painter, option, widget):
        width, height = s(self.world.length), s(self.world.width)
        line = s(self.world.line_width)

        # Save transformation:
        old_transformation = painter.worldTransform()

        # Change position
        painter.translate(-width / 2, -height / 2)

        painter.setBrush(WHITE)
        painter.setPen(WHITE)

        # Center
        draw_arc(width / 2, height / 2, 0, 1.5 * line, 0, 360, painter)

        # Sides
        painter.drawRect(0.0, 0.0, line, height)
        painter.drawRect(width - line, 0.0, line, height)
        painter.drawRect(0.0, 0.0, width, line)
        painter.drawRect(0.0, height - line, width, line)

        # Central lines
        radius = s(self.world.center_radius)
        #painter.fillRect((width - line) / 2, 0, line, height, WHITE)
        # XXX: why did I need to double the line width?
        painter.fillRect(width / 2 - line, 0, 2 * line, height, WHITE)
        draw_arc(width / 2, height / 2, radius - line, radius, 0, 360, painter)

        # Defense lines
        dradius = s(self.world.defense_radius)
        dstretch = s(self.world.defense_stretch)

        painter.drawRect(dradius - line, (height - dstretch) / 2, line, dstretch)
        draw_arc(0, (height - dstretch) / 2, dradius - line, dradius, 0, 90, painter)
        draw_arc(0, (height + dstretch) / 2, dradius - line, dradius, 270, 360, painter)

        painter.drawRect(width - dradius, (height - dstretch) / 2, line, dstretch)
        draw_arc(width, (height - dstretch) / 2, dradius - line, dradius, 90, 180, painter)
        draw_arc(width, (height + dstretch) / 2, dradius - line, dradius, 180, 270, painter)

        # Penalty
        penalty_spot = s(self.world.penalty_spot_distance)
        draw_arc(penalty_spot, height / 2, 0, line, 0, 360, painter)
        draw_arc(width - penalty_spot, height / 2, 0, line, 0, 360, painter)

        # Goals
        gwidth = s(self.world.goal_width)
        gdepth = s(self.world.goal_depth)
        gline = s(self.world.goal_wall_width)

        painter.drawRect(-gdepth - gline, (height - gwidth) / 2 - gline, gdepth + gline, gline)
        painter.drawRect(-gdepth - gline, (height - gwidth) / 2, gline, gwidth)
        painter.drawRect(-gdepth - gline, (height + gwidth) / 2, gdepth + gline, gline)

        painter.drawRect(width, (height - gwidth) / 2 - gline, gdepth + gline, gline)
        painter.drawRect(width + gdepth, (height - gwidth) / 2, gline, gwidth)
        painter.drawRect(width, (height + gwidth) / 2, gdepth + gline, gline)

        # Reset transformation
        painter.setTransform(old_transformation)


class BallItem(QGraphicsItem):

    def __init__(self, ball):
        super(BallItem, self).__init__()
        self.ball = ball

    @property
    def uuid(self):
        return BALL

    def boundingRect(self):
        radius = s(self.ball.radius)
        return QRectF(-2 * radius, -2 * radius, 4 * radius, 4 * radius)

    def position(self):
        x, y, width, height = s(self.ball.x, self.ball.y, self.ball.world.length, self.ball.world.width)
        #self.setPos(x - width / 2, -y - height / 2)
        self.setPos(x, -y)

    def paint(self, painter, option, widget=None):
        #setPos( robot->x() - robot->stage()->fieldLength()/2 , -robot->y() - robot->stage()->fieldWidth()/2 );

        # Save transformation:
        old_transformation = painter.worldTransform()

        painter.setBrush(ORANGE)
        painter.setPen(ORANGE)
        radius = s(self.ball.radius)
        painter.drawEllipse(-radius, -radius, 2 * radius, 2 * radius)

        #QGraphicsEllipseItem* bola = new QGraphicsEllipseItem(
        #        field->pos().x() + (stage->ball()->x() - BALL_RADIUS/2),
        #        field->pos().y() + (stage->ball()->y() - BALL_RADIUS),
        #        BALL_RADIUS,BALL_RADIUS,NULL);

        #bola->setBrush(QBrush(orange));
        #bola->setPen(QPen(orange));

        #painter.drawLine(0, 0, self.radius * cos(self.angle), self.radius * sin(self.angle))
        #painter.drawText(0, 0, "Teste")

        # Reset transformation
        painter.setTransform(old_transformation)


class StageView(QGraphicsView):
    def __init__(self, parent=None):
        super(StageView, self).__init__(parent)

        #self.setViewport(QGLWidget(QGLFormat(QGL.SampleBuffers)))
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.setBackgroundBrush(QBrush(FIELD_GREEN))
        self.setCacheMode(QGraphicsView.CacheNone)
        self.setScene(QGraphicsScene(0, 0, 0, 0))
        self._world = None

    @property
    def world(self):
        return self._world

    @world.setter
    def world(self, w):
        self._world = w
        width, height = s(w.length), s(w.width)
        self.setScene(QGraphicsScene(-width / 2, -height / 2, width, height))
        #self.setScene(QGraphicsScene(-w.width / 2, -w.length / 2, w.width, w.length))
        #self.scale(1, -1)

    def redraw(self):
        # TODO: only do this when geometry changes
        self.scene().clear()
        self.world = self.world

        # TODO this seems bad, something more performatic is desired
        scene = self.scene()
        scene.clear()
        with self.world as w:
            field = FieldItem(w)
            scene.addItem(field)
            width, height = s(self.world.length), s(self.world.width)
            #field.setPos(-width / 2, -height / 2)
            #field.setPos(BORDER / 2, BORDER / 2)
            field.setPos(0, 0)

            ball = BallItem(w.ball)
            scene.addItem(ball)
            ball.position()

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

            self.fitInView(-width / 2 - BORDER, -height / 2 - BORDER, width + 2 * BORDER, height + 2 * BORDER, Qt.KeepAspectRatio)
