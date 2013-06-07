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
        self.setFlags(QGraphicsItem.ItemIsSelectable|QGraphicsItem.ItemIsFocusable)

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
        painter.save();

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
        painter.restore();


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
        boundary = s(self.world.boundary_width + self.world.referee_width)
        return QRectF(-width / 2.0 - boundary, -height / 2.0 - boundary, width + 2 * boundary, height + 2 * boundary);

    def position(self):
        self.setPos(0, 0)

    def paint(self, painter, option, widget):
        width, height = s(self.world.length), s(self.world.width)
        line = s(self.world.line_width)

        # Save transformation:
        painter.save();

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
        painter.fillRect((width - line) / 2, 0, line, height, WHITE)
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
        painter.restore();


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
        painter.save();

        painter.setBrush(ORANGE)
        painter.setPen(ORANGE)
        radius = s(self.ball.radius)
        painter.drawEllipse(-radius, -radius, 2 * radius, 2 * radius)

        # Reset transformation
        painter.restore();


class StageView(QGraphicsView):
    def __init__(self, parent=None):
        super(StageView, self).__init__(parent)

        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.setBackgroundBrush(QBrush(FIELD_GREEN))
        self.setCacheMode(QGraphicsView.CacheNone)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setScene(QGraphicsScene(0, 0, 0, 0))
        self._world = None

        # Set the zoom so the view doesn't starts all zoomed
        self.scale(1.0 / 15, 1.0 / 15)

        self.setDragMode(QGraphicsView.ScrollHandDrag)              # Set mouse drag to click and drag
        self.setFocusPolicy(Qt.WheelFocus)                          # Set focus on view when tabbing, clicking and scrolling the wheel
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)    # Disable horizontal and vertical scrollbars
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.setInteractive(True)   # Set interactive so user can click to focus a robot

    @property
    def world(self):
        return self._world

    @world.setter
    def world(self, w):
        self._world = w
        self._width, self._height = s(w.length), s(w.width)
        self.setScene(QGraphicsScene(-1.5 * self._width, -1.5 * self._height, 3 * self._width, 3 * self._height))

    # Mouse wheel to zoom
    def wheelEvent(self, event):
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        scaleFactor = 1.10
        if event.delta() > 0:
            self.scale(scaleFactor, scaleFactor)
        else:
            self.scale(1.0 / scaleFactor, 1.0 / scaleFactor)

    # Handle key events
    def keyPressEvent(self, event):
        # Space key resets the view
        if event.key() == Qt.Key_Space:
            self.fitInView(-self._width / 2, -self._height / 2, self._width, self._height, Qt.KeepAspectRatio)

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
