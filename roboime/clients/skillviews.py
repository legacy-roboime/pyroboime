from PyQt4.QtGui import QGraphicsItem
from PyQt4.QtCore import QRectF
from collections import OrderedDict
from numpy import array

from ..utils.mathutils import sin, cos
from .qtutils import scale as s
from .qtutils import draw_x, draw_arrow_line
from .qtutils import BLACK, RED, BLUE, GREEN, TRANSPARENT, PINK, LIGHT_BLUE
from ..core.skills import goto, gotoavoid, driveto

_view_table = {}


def view_for(mapped_skill):
    def _view_for(view_class):
        _view_table[mapped_skill] = view_class
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


@view_for(goto.Goto)
class GotoView(SkillView):

    def __init__(self, skill, draw_forces=True, **kwargs):
        super(GotoView, self).__init__(skill, **kwargs)
        self.draw_forces = draw_forces

    def boundingRect(self):
        m = self.margin
        x, y = self.relative_point(self.robot)
        return QRectF(-m, -m, x + m, y + m)

    def paint(self, painter, option, widget=None):
        # Save transformation:
        painter.save()

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

        if self.draw_forces:
            # draw an arrow for every repulsion force
            painter.setPen(PINK)
            for force in self.skill.other_forces():
                fx, fy = force
                draw_arrow_line(painter, 0, 0, fx, -fy, m)

            # draw an arrow for attraction force
            painter.setPen(LIGHT_BLUE)
            force = self.skill.attraction_force()
            fx, fy = force
            #draw_arrow_line(painter, 0, 0, fx, -fy, m)

        # Reset transformation
        painter.restore()


@view_for(gotoavoid.GotoAvoid)
class GotoAvoidView(GotoView):

    def __init__(self, *args, **kwargs):
        super(GotoAvoidView, self).__init__(*args, **kwargs)
        self.target = (0, 0)

    def boundingRect(self):
        m = self.margin
        x, y = self.relative_point(self.target)
        return QRectF(-m, -m, x + m, y + m)

    def paint(self, painter, option, widget=None):
        super(GotoAvoidView, self).paint(painter, option, widget)

        # Save transformation:
        painter.save()

        #p1 = array(self.skill.base_point)
        #p2 = array([cos(self.skill.base_angle), sin(self.skill.base_angle)]) * self.skill.threshold
        #self.target = p1 + p2
        self.target = self.skill.target

        x, y = self.relative_point(self.target)
        m = self.margin

        # draw an X on the target
        painter.setBrush(BLUE)
        painter.setPen(BLUE)
        draw_x(painter, x, y, m)

        painter.setBrush(TRANSPARENT)
        painter.setPen(GREEN)
        x, y = self.relative_point(self.skill.world.ball)
        avr = s(self.skill.avoid_radius)
        painter.drawEllipse(x - avr, y - avr, 2 * avr, 2 * avr)

        # Reset transformation
        painter.restore()


@view_for(driveto.DriveTo)
class DriveToView(GotoAvoidView):

    def __init__(self, *args, **kwargs):
        super(DriveToView, self).__init__(*args, **kwargs)
        self.target = (0, 0)

    def boundingRect(self):
        m = self.margin
        x, y = self.relative_point(self.target)
        return QRectF(-m, -m, x + m, y + m)

    def paint(self, painter, option, widget=None):
        super(DriveToView, self).paint(painter, option, widget)

        # Save transformation:
        painter.save()

        p1 = array(self.skill.base_point)
        p2 = array([cos(self.skill.base_angle), sin(self.skill.base_angle)]) * self.skill.threshold
        self.target = p1 + p2

        x, y = self.relative_point(self.target)
        m = self.margin

        # draw an X on the target
        painter.setBrush(BLUE)
        painter.setPen(BLUE)
        draw_x(painter, x, y, m)

        # Reset transformation
        painter.restore()


_weighted_view_table = []
for skill, view in _view_table.iteritems():
    weight = 0
    for _skill in _view_table.iterkeys():
        if issubclass(skill, _skill):
            weight += 1
    _weighted_view_table.append((weight, skill, view))
_weighted_view_table.sort(reverse=True)
view_table = OrderedDict((skill, view) for (_, skill, view) in _weighted_view_table)


def view_selector(skill, use_fallback=True):
    """Will return an instance of the propert view."""
    # try to use the view directly associated with this skill
    direct_view = view_table.get(skill)
    if direct_view is not None:
        return direct_view(skill)
    # if none is found and a fallback is desired, search the view_table
    # for a compatible view
    elif use_fallback:
        for s, view in view_table.iteritems():
            if isinstance(skill, s):
                return view(skill)
