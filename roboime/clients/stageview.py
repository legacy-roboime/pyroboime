from PyQt4.QtGui import QGraphicsView, QColor, QBrush, QGraphicsScene
from PyQt4.QtCore import Qt

from .qtutils import scale as s
from . import worldviews
from . import skillviews
from . import tacticviews


# colors
FIELD_GREEN = Qt.darkGreen
GREEN = Qt.green
BLUE = Qt.blue
YELLOW = Qt.yellow
BLACK = Qt.black
WHITE = Qt.white
LIGHT_GREY = QColor(0xcc, 0xcc, 0xcc)
ORANGE = QColor(0xff, 0xbb, 0x00)


class StageView(QGraphicsView):
    def __init__(self, parent=None):
        super(StageView, self).__init__(parent)
        self.setBackgroundBrush(QBrush(FIELD_GREEN))
        self.setScene(QGraphicsScene(0, 0, 0, 0))
        self._world = None
        self.scale(1.0 / 15, 1.0 / 15)

    @property
    def world(self):
        return self._world

    @world.setter
    def world(self, w):
        self._world = w
        width, height = s(w.length), s(w.width)
        self.setScene(QGraphicsScene(-1.5 * width, -1.5 * height, 3 * width, 3 * height))

    # Mouse wheel to zoom
    def wheelEvent(self, event):
        scaleFactor = 1.10
        if event.delta() > 0:
            self.scale(scaleFactor, scaleFactor)
        else:
            self.scale(1.0 / scaleFactor, 1.0 / scaleFactor)

    # Resize the view to fit the screen
    def fit(self):
        boundary = self._world.boundary_width + self._world.referee_width
        self.fitInView(-s(self._world.length / 2 + boundary),
            -s(self._world.width / 2 + boundary),
            s(self._world.length + 2 * boundary),
            s(self._world.width + 2 * boundary),
            Qt.KeepAspectRatio)

    # Handle key events
    def keyPressEvent(self, event):
        # Resets the view
        if event.key() == Qt.Key_Space:
            self.fit()

    def redraw(self):
        # TODO: only do this when geometry changes
        # clear the old scene
        self.scene().clear()
        self.world = self.world

        # TODO this seems bad, something more performatic is desired
        scene = self.scene()
        scene.clear()

        with self.world as w:
            field = worldviews.FieldView(w)
            field.position()
            scene.addItem(field)

            robots = w.robots

            for r in robots:
                # draw the robot
                robot = worldviews.RobotView(r)
                robot.position()
                scene.addItem(robot)

            for r in robots:
                # draw the robot ids
                robotid = worldviews.RobotIdView(r)
                robotid.position()
                scene.addItem(robotid)

            for r in robots:
                # draw the skill
                skill = skillviews.view_selector(r.skill)
                if skill is not None:
                    skill.position()
                    scene.addItem(skill)

            for r in robots:
                # draw the tactic
                tactic = tacticviews.view_selector(r.tactic)
                if tactic is not None:
                    tactic.position()
                    scene.addItem(tactic)

            ball = worldviews.BallView(w.ball)
            ball.position()
            scene.addItem(ball)
