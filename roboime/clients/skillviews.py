from PyQt4.QtGui import QGraphicsItem, QGraphicsView, QColor, QBrush, QPainter, QGraphicsScene, QPainterPath, QFont
from PyQt4.QtCore import QRectF, Qt, QString

from .qtutils import scale as s
from ..core.skills import goto


BLACK = Qt.black


class SkillView(QGraphicsItem):
    def __init__(self, skill):
        super(SkillView, self).__init__()
        self.skill = skill
        self.margin = 5

    def position(self):
        x, y = s(self.skill.robot)
        self.setPos(x, -y)


class GotoView(SkillView):
    def __init__(self, goto, **kwargs):
        super(GotoView, self).__init__(goto, **kwargs)

    def relative_point(self):
        x, y = s(self.skill.robot)
        fx, fy = s(self.skill.final_target)
        return fx - x, -(fy - y)

    def boundingRect(self):
        m = self.margin
        x, y = self.relative_point()
        return QRectF(-m, -m, x + m, y + m)

    def paint(self, painter, option, widget=None):
        # Save transformation:
        old_transformation = painter.worldTransform()

        painter.setBrush(BLACK)
        painter.setPen(BLACK)

        x, y = self.relative_point()
        painter.drawLine(0, 0, x, y)

        # Reset transformation
        painter.setTransform(old_transformation)


def view_selector(skill):
    """Will return an instance of the propert view."""
    if isinstance(skill, goto.Goto):
        return GotoView(skill)
