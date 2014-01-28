#
# Copyright (C) 2013 RoboIME
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
from PyQt4.QtGui import QGraphicsItem, QFont
from PyQt4.QtCore import QRectF
from collections import OrderedDict
from numpy.linalg import norm
from numpy import array

from ..utils.mathutils import sin, cos
from .qtutils import scale as s
from .qtutils import draw_x, draw_arrow_line
from .qtutils import BLACK, RED, BLUE, GREEN, TRANSPARENT, PINK, LIGHT_BLUE
from ..core import Skill
from ..core.skills import goto, gotoavoid, driveto, drivetoball

_view_table = {}


def view_for(mapped_model):
    def _view_for(view_class):
        _view_table[mapped_model] = view_class
        return view_class
    return _view_for


@view_for(Skill)
class SkillView(QGraphicsItem):

    def __init__(self, skill):
        super(SkillView, self).__init__()
        self.skill = skill
        self.margin = 5

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

    def boundingRect(self):
        return QRectF(-10, -140, 200, 0)

    def paint(self, painter, option, widget=None):
        # Save transformation:
        painter.save()

        painter.setBrush(BLACK)
        painter.setPen(BLACK)
        painter.setFont(QFont('Courier', 72, 2))

        skill = str(self.skill)
        painter.drawText(-10, -90, skill)

        # Reset transformation
        painter.restore()


@view_for(goto.Goto)
class GotoView(SkillView):

    draw_forces = False
    #draw_forces = True

    def __init__(self, skill, **kwargs):
        super(GotoView, self).__init__(skill, **kwargs)

    def boundingRect(self):
        m = self.margin
        x, y = self.relative_point(self.robot)
        return QRectF(-m, -m, x + m, y + m)

    def paint(self, painter, option, widget=None):
        super(GotoView, self).paint(painter, option, widget)

        # Save transformation:
        painter.save()

        x, y = self.relative_point(self.skill.final_target)
        m = self.margin

        # draw a line from robot to its target
        painter.setBrush(BLACK)
        painter.setPen(BLACK)
        #FIXME: float() casting because sometimes x or y can become numpy.float64
        # Should be fixed with a proper API design
        painter.drawLine(0, 0, float(x), float(y))

        # draw an X on the target
        painter.setBrush(RED)
        painter.setPen(RED)
        draw_x(painter, x, y, m)

        if self.draw_forces:
            forces = list(self.skill.other_forces())
            #scale = 0.07
            scale = 0.01

            attraction_force = self.skill.attraction_force()
            if norm(attraction_force) < self.skill.min_force_to_ignore_others:
                # draw an arrow for every delta speed force
                painter.setPen(BLACK)
                for (_, _, force) in forces:
                    fx, fy = force * scale
                    if (fx ** 2 + fy ** 2) > 2 * m ** 2:
                        draw_arrow_line(painter, 0, 0, fx, -fy, m)

                # draw an arrow for every repulsion force
                painter.setPen(PINK)
                for (force, _, _) in forces:
                    fx, fy = force * scale
                    if (fx ** 2 + fy ** 2) > 2 * m ** 2:
                        draw_arrow_line(painter, 0, 0, fx, -fy, m)

                # draw an arrow for every magnetic force
                painter.setPen(RED)
                for (_, force, _) in forces:
                    fx, fy = force * scale
                    if (fx ** 2 + fy ** 2) > 2 * m ** 2:
                        draw_arrow_line(painter, 0, 0, fx, -fy, m)

                # draw an arrow for attraction force
                painter.setPen(LIGHT_BLUE)
                force = attraction_force
                fx, fy = force * scale
                draw_arrow_line(painter, 0, 0, fx, -fy, m)

            else:
                # draw an X for attraction force
                painter.setPen(LIGHT_BLUE)
                draw_x(painter, 0, 0, s(self.robot.radius))

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

@view_for(drivetoball.DriveToBall)
class DriveToBallView(DriveToView):
    # TODO: this.
    def __init__(self, *args, **kwargs):
        super(DriveToView, self).__init__(*args, **kwargs)
        self.target = (0, 0)

    def boundingRect(self):
        m = self.margin
        x, y = self.relative_point(self.target)
        return QRectF(-m, -m, x + m, y + m)

    def paint(self, painter, option, widget=None):
        super(DriveToBallView, self).paint(painter, option, widget)

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
