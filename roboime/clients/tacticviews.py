from PyQt4.QtGui import QGraphicsItem
from PyQt4.QtCore import QRectF
from collections import OrderedDict

from .qtutils import scale as s
from .qtutils import RED, BLUE
from ..core.tactics import blocker
from ..core.tactics import zickler43


view_table = OrderedDict()


def view_for(mapped_tactic):
    # TODO: make this resolve dependencies
    def _view_for(view_class):
        view_table[mapped_tactic] = view_class
        return view_class
    return _view_for


class TacticView(QGraphicsItem):

    def __init__(self, tactic):
        super(TacticView, self).__init__()
        self.tactic = tactic
        self.margin = 20

    def position(self):
        x, y = s(self.tactic.robot)
        self.setPos(x, -y)


@view_for(blocker.Blocker)
class BlockerView(TacticView):

    def relative_goto_point(self):
        x, y = s(self.tactic.robot)
        fx, fy = s(self.tactic.goto.final_target)
        return fx - x, -(fy - y)

    def relative_target_point(self):
        x, y = s(self.tactic.robot)
        fx, fy = s(self.tactic.blockpoint)
        return fx - x, -(fy - y)

    def boundingRect(self):
        m = self.margin
        x, y = self.relative_target_point()
        return QRectF(-m, -m, x + m, y + m)

    def paint(self, painter, option, widget=None):
        # Save transformation:
        painter.save();

        gx, gy = self.relative_goto_point()
        bx, by = self.relative_target_point()
        #m = self.margin

        # draw a line from robot to its target
        painter.setBrush(BLUE)
        painter.setPen(BLUE)
        painter.drawLine(gx, gy, bx, by)

        # draw an X on the target
        #painter.setBrush(RED)
        #painter.setPen(RED)
        #painter.drawLine(x - m, y - m, x + m, y + m)
        #painter.drawLine(x - m, y + m, x + m, y - m)

        # Reset transformation
        painter.restore();


@view_for(zickler43.Zickler43)
class Zickler43View(TacticView):

    def relative_goto_point(self):
        x, y = s(self.tactic.robot)
        fx, fy = s(self.tactic.current_state.final_target)
        return fx - x, -(fy - y)

    def relative_target_point(self):
        x, y = s(self.tactic.robot)
        fx, fy = s(self.tactic.lookpoint)
        return fx - x, -(fy - y)

    def boundingRect(self):
        m = self.margin
        x, y = self.relative_target_point()
        return QRectF(-m, -m, x + m, y + m)

    def paint(self, painter, option, widget=None):
        # Save transformation:
        painter.save();

        gx, gy = self.relative_goto_point()
        bx, by = self.relative_target_point()
        #m = self.margin

        # draw a line from robot to its target
        painter.setBrush(RED)
        painter.setPen(RED)
        painter.drawLine(gx, gy, bx, by)

        # draw an X on the target
        #painter.setBrush(RED)
        #painter.setPen(RED)
        #painter.drawLine(x - m, y - m, x + m, y + m)
        #painter.drawLine(x - m, y + m, x + m, y - m)

        # Reset transformation
        painter.restore();


def view_selector(tactic):
    """Will return an instance of the propert view."""
    for t, view in view_table.iteritems():
        if isinstance(tactic, t):
            return view(tactic)
