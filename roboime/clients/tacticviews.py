from PyQt4.QtGui import QGraphicsItem, QFont
from PyQt4.QtCore import QRectF
from collections import OrderedDict

from .qtutils import scale as s
#from .qtutils import draw_x
from .qtutils import RED, BLUE, BLACK
from ..core import Tactic
from ..core.tactics.blocker import Blocker
from ..core.tactics.zickler43 import Zickler43

_view_table = {}


def view_for(mapped_model):
    def _view_for(view_class):
        _view_table[mapped_model] = view_class
        return view_class
    return _view_for


@view_for(Tactic)
class TacticView(QGraphicsItem):

    def __init__(self, tactic):
        super(TacticView, self).__init__()
        self.tactic = tactic
        self.margin = 20

    @property
    def robot(self):
        return self.tactic.robot

    def position(self):
        x, y = s(self.robot)
        self.setPos(x, -y)

    def relative_point(self, point):
        x, y = s(self.robot)
        fx, fy = s(point)
        return fx - x, -(fy - y)

    def boundingRect(self):
        return QRectF(-10, -140, 200, 0)

    def paint(self, painter, option, widget=None):
        # Save transformation:
        painter.save()

        painter.setBrush(BLACK)
        painter.setPen(BLACK)
        painter.setFont(QFont('Courier', 72, 2))

        tactic = str(self.tactic)
        painter.drawText(-10, -140, tactic)

        #state = str(self.tactic.current_state)
        #painter.drawText(-10, -90, state)

        # Reset transformation
        painter.restore()


#@view_for(Blocker)
class BlockerView(TacticView):

    def boundingRect(self):
        m = self.margin
        x, y = self.relative_point(self.tactic.goto.final_target)
        return QRectF(-m, -m, x + m, y + m)

    def paint(self, painter, option, widget=None):
        super(BlockerView, self).paint(painter, option, widget)

        # Save transformation:
        painter.save()

        gx, gy = self.relative_point(self.tactic.goto.final_target)
        bx, by = self.relative_point(self.tactic.blockpoint)
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
        painter.restore()


#@view_for(Zickler43)
class Zickler43View(TacticView):

    def boundingRect(self):
        m = self.margin
        x, y = self.relative_point(self.tactic.current_state.final_target)
        return QRectF(-m, -m, x + m, y + m)

    def paint(self, painter, option, widget=None):
        super(Zickler43View, self).paint(painter, option, widget)

        # Save transformation:
        painter.save()

        #gx, gy = self.relative_point(self.tactic.goto.final_target)
        gx, gy = self.relative_point(self.robot.ball)
        bx, by = self.relative_point(self.tactic.lookpoint)
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
        painter.restore()


_weighted_view_table = []
for model, view in _view_table.iteritems():
    weight = 0
    for _model in _view_table.iterkeys():
        if issubclass(model, _model):
            weight += 1
    _weighted_view_table.append((weight, model, view))
_weighted_view_table.sort(reverse=True)
view_table = OrderedDict((model, view) for (_, model, view) in _weighted_view_table)


def view_selector(model, use_fallback=True):
    """Will return an instance of the propert view."""
    # try to use the view directly associated with this model
    direct_view = view_table.get(model)
    if direct_view is not None:
        return direct_view(model)
    # if none is found and a fallback is desired, search the view_table
    # for a compatible view
    elif use_fallback:
        for s, view in view_table.iteritems():
            if isinstance(model, s):
                return view(model)
