from PyQt4.QtGui import QGraphicsItem
from PyQt4.QtCore import QRectF
from collections import OrderedDict
from numpy import array

from ..utils.mathutils import sin, cos
from .qtutils import scale as s
from .qtutils import draw_x
from .qtutils import BLACK, RED, BLUE, GREEN, TRANSPARENT
from ..core.skills import goto, gotoavoid

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

    @property
    def robot(self):
        return self.skill.robot

    def position(self):
        x, y = s(self.robot)
        self.setPos(x, -y)

    def relative_point(self, point):
        x, y = s(self.robot)
        fx, fy = s(point)
        return fx - x, -(fy - y)


@view_for(gotoavoid.GotoAvoid)
class GotoAvoidView(SkillView):

    def __init__(self, *args, **kwargs):
        super(GotoAvoidView, self).__init__(*args, **kwargs)
        self.target = (0, 0)

    def boundingRect(self):
        m = self.margin
        x, y = self.relative_point(self.target)
        return QRectF(-m, -m, x + m, y + m)

    def paint(self, painter, option, widget=None):
        # Save transformation:
        painter.save();

        p1 = array(self.skill.base_point)
        p2 = array([cos(self.skill.base_angle), sin(self.skill.base_angle)]) * self.skill.threshold
        self.target = p1 + p2

        x, y = self.relative_point(self.target)
        m = self.margin

        # draw a line from robot to its target
        painter.setBrush(BLACK)
        painter.setPen(BLACK)
        painter.drawLine(0, 0, x, y)

        # draw an X on the target
        painter.setBrush(BLUE)
        painter.setPen(BLUE)
        draw_x(painter, x, y, m)

        painter.setBrush(TRANSPARENT)
        painter.setPen(GREEN)
        x, y = self.relative_point(self.skill.world.ball)
        avr = s(self.skill.avoid_radius)
        painter.drawEllipse(x - avr, y - avr, 2 * avr, 2 * avr)

        # draw an X on the target
        x, y = self.relative_point(self.skill.final_target)
        painter.setBrush(RED)
        painter.setPen(RED)
        draw_x(painter, x, y, m)

        # Reset transformation
        painter.restore();


@view_for(goto.Goto)
class GotoView(SkillView):

    def boundingRect(self):
        m = self.margin
        x, y = self.relative_point(self.robot)
        return QRectF(-m, -m, x + m, y + m)

    def paint(self, painter, option, widget=None):
        # Save transformation:
        painter.save();

        x, y = self.relative_point(self.skill.final_target)
        m = self.margin

        # draw a line from robot to its target
        painter.setBrush(BLACK)
        painter.setPen(BLACK)
        painter.drawLine(0, 0, x, y)

        # draw an X on the target
        painter.setBrush(RED)
        painter.setPen(RED)
        draw_x(painter, x, y, m)

        # Reset transformation
        painter.restore();


def view_selector(skill):
    """Will return an instance of the propert view."""
    for s, view in view_table.iteritems():
        if isinstance(skill, s):
            return view(skill)
