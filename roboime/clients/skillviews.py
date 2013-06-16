from PyQt4.QtGui import QGraphicsItem
from PyQt4.QtCore import QRectF, Qt
from collections import OrderedDict

from .qtutils import scale as s
from ..core.skills import goto


BLACK = Qt.black
GREEN = Qt.green
RED = Qt.red


view_table = OrderedDict()


def view_for(mapped_skill):
    # TODO: make this resolve dependencies
    def _view_for(view_class):
        view_table[mapped_skill] = view_class
        return view_class
    return _view_for


class SkillView(QGraphicsItem):
    def __init__(self, skill):
        super(SkillView, self).__init__()
        self.skill = skill
        self.margin = 20

    def position(self):
        x, y = s(self.skill.robot)
        self.setPos(x, -y)


@view_for(goto.Goto)
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
        painter.save();

        x, y = self.relative_point()
        m = self.margin

        # draw a line from robot to its target
        painter.setBrush(BLACK)
        painter.setPen(BLACK)
        painter.drawLine(0, 0, x, y)

        # draw an X on the target
        painter.setBrush(RED)
        painter.setPen(RED)
        painter.drawLine(x - m, y - m, x + m, y + m)
        painter.drawLine(x - m, y + m, x + m, y - m)

        # Reset transformation
        painter.restore();


def view_selector(skill):
    """Will return an instance of the propert view."""
    for s, view in view_table.iteritems():
        if isinstance(skill, s):
            return view(skill)
