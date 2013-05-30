from PyQt4.QtGui import QGraphicsItem, QGraphicsView, QColor, QBrush, QPainter, QGraphicsScene, QPainterPath, QFont
from PyQt4.QtCore import QRectF, Qt, QString

from .qtutils import scale as s
from ..utils.mathutils import sin, cos, acos
from . import skillviews

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
LIGHT_GREY = QColor(0xcc, 0xcc, 0xcc)
ORANGE = QColor(0xff, 0xbb, 0x00)


class RobotItem(QGraphicsItem):
    def __init__(self, robot):
        super(RobotItem, self).__init__()
        self.robot = robot
        self.outline = QPainterPath()

    @property
    def uuid(self):
        return self.robot.uuid

    @property
    def color(self):
        if self.isSelected():
            return GREEN
        elif self.robot.is_blue:
            return BLUE
        elif self.robot.is_yellow:
            return YELLOW
        else:
            return BLACK

    def position(self):
        x, y, width, height = s(self.robot.x, self.robot.y, self.robot.world.length, self.robot.world.width)
        radius = s(self.robot.radius)

        self.cut_angle = acos(self.robot.front_cut / self.robot.radius)

        self.outline.moveTo(radius, 0)
        self.outline.arcTo(-radius, -radius, 2 * radius, 2 * radius, 0, 360 - 2 * self.cut_angle)
        self.outline.closeSubpath()

        self.setPos(x, -y)

    def boundingRect(self):
        radius = s(self.robot.radius)
        return QRectF(-radius, -radius, 2 * radius, 2 * radius)

    def paint(self, painter, option, widget=None):
        # Save transformation:
        old_transformation = painter.worldTransform()

        color = self.color

        # Change position
        painter.setBrush(color)
        painter.setPen(color)
        robot_rotation = self.robot.angle

        # Draw robot shape
        painter.rotate(-self.cut_angle - robot_rotation)
        painter.drawPath(self.outline)
        painter.rotate(self.cut_angle + robot_rotation)

        # Draw id
        robot_id = QString('?')
        robot_id.setNum(self.robot.uid)
        painter.setBrush(BLACK)
        painter.setPen(BLACK)
        painter.setFont(QFont('Courier', 132, 2, False))
        painter.drawText(-90, -210, 1000, 1000, 0, robot_id)

        # Reset transformation
        painter.setTransform(old_transformation)


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

    def position(self):
        self.setPos(0, 0)

    def paint(self, painter, option, widget):
        width, height = s(self.world.length), s(self.world.width)
        line = s(self.world.line_width)

        # Save transformation:
        old_transformation = painter.worldTransform()

        # Change position
        painter.translate(-width / 2, -height / 2)

        # Boundaries
        painter.setBrush(LIGHT_GREY)
        painter.setPen(LIGHT_GREY)
        boundary = s(self.world.boundary_width + self.world.referee_width)
        painter.drawRect(-boundary, -boundary, 2 * line, height + 2 * boundary)
        painter.drawRect(width + boundary - 2 * line, -boundary, 2 * line, height + 2 * boundary)
        painter.drawRect(-boundary, -boundary, width + 2 * boundary, 2 * line)
        painter.drawRect(-boundary, boundary + height - 2 * line, width + 2 * boundary, 2 * line)

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
        self.setPos(x, -y)

    def paint(self, painter, option, widget=None):

        # Save transformation:
        old_transformation = painter.worldTransform()

        painter.setBrush(ORANGE)
        painter.setPen(ORANGE)
        radius = s(self.ball.radius)
        painter.drawEllipse(-radius, -radius, 2 * radius, 2 * radius)

        # Reset transformation
        painter.setTransform(old_transformation)


class StageView(QGraphicsView):
    def __init__(self, parent=None):
        super(StageView, self).__init__(parent)

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

    def redraw(self):
        # TODO: only do this when geometry changes
        # clear the old scene
        self.scene().clear()
        self.world = self.world

        # TODO this seems bad, something more performatic is desired
        scene = self.scene()
        scene.clear()

        with self.world as w:
            field = FieldItem(w)
            field.position()
            scene.addItem(field)

            width, height = s(self.world.length), s(self.world.width)
            border = s(self.world.boundary_width + self.world.referee_width)

            ball = BallItem(w.ball)
            ball.position()
            scene.addItem(ball)

            for r in w.iterrobots():
                # draw the robot
                robot = RobotItem(r)
                robot.position()
                scene.addItem(robot)

            for r in w.iterrobots():
                # draw the skill
                skill = skillviews.view_selector(r.skill)
                if skill is not None:
                    skill.position()
                    scene.addItem(skill)

            self.fitInView(-width / 2 - border, -height / 2 - border, width + 2 * border, height + 2 * border, Qt.KeepAspectRatio)
