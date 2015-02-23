#
# Copyright (C) 2013-2015 RoboIME
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
from PyQt4.QtGui import QGraphicsItem, QPainterPath, QFont
from PyQt4.QtCore import QRectF, QString

from .qtutils import scale as s
from .qtutils import draw_arc
from .qtutils import BLACK, BLUE, GREEN, YELLOW, LIGHT_GREY, ORANGE, WHITE

from ..utils.mathutils import acos


# some known uuids
BALL = 0xba11
FIELD = 0xf1e1d


class RobotIdView(QGraphicsItem):
    def __init__(self, robot):
        super(RobotIdView, self).__init__()
        self.robot = robot

    def boundingRect(self):
        return QRectF(-80, -80, 160, 160)

    def position(self):
        x, y = s(self.robot)
        self.setPos(x, -y)

    def paint(self, painter, option, widget=None):
        # Draw id
        painter.save()
        robot_id = QString('?')
        robot_id.setNum(self.robot.uid)
        painter.setBrush(BLACK)
        painter.setPen(BLACK)
        painter.setFont(QFont('Courier', 132, 2))
        painter.drawText(-90, -90, robot_id)
        painter.restore()


class RobotView(QGraphicsItem):
    def __init__(self, robot):
        super(RobotView, self).__init__()
        self.robot = robot
        self.outline = QPainterPath()
        self.cut_angle = 0.0
        self.setFlags(QGraphicsItem.ItemIsSelectable)

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

        self.outline = QPainterPath()
        self.outline.moveTo(radius, 0)
        self.outline.arcTo(-radius, -radius, 2 * radius, 2 * radius, 0, 360 - 2 * self.cut_angle)
        self.outline.closeSubpath()

        self.setPos(x, -y)

    def boundingRect(self):
        radius = s(self.robot.radius)
        return QRectF(-radius, -radius, 2 * radius, 2 * radius)

    def paint(self, painter, option, widget=None):
        # Save transformation:
        painter.save()

        color = self.color

        # Change position
        painter.setBrush(color)
        painter.setPen(color)

        robot_rotation = self.robot.angle or 0.0
        # Draw robot shape
        painter.rotate(-self.cut_angle - robot_rotation)
        painter.drawPath(self.outline)
        painter.rotate(self.cut_angle + robot_rotation)

        # Reset transformation
        painter.restore()


class FieldView(QGraphicsItem):

    def __init__(self, world):
        super(FieldView, self).__init__()
        self.world = world

    @property
    def uuid(self):
        return FIELD

    def boundingRect(self):
        width, height = s(self.world.length), s(self.world.width)
        boundary = s(self.world.boundary_width + self.world.referee_width)
        return QRectF(-width / 2.0 - boundary, -height / 2.0 - boundary, width + 2 * boundary, height + 2 * boundary)

    def position(self):
        self.setPos(0, 0)

    def paint(self, painter, option, widget):
        width, height = s(self.world.length), s(self.world.width)
        line = s(self.world.line_width)

        # Save transformation:
        painter.save()

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

        if self.world.left_goal.is_blue:
            painter.setBrush(BLUE)
            painter.setPen(BLUE)
        else:
            painter.setBrush(YELLOW)
            painter.setPen(YELLOW)
        painter.drawRect(-gdepth - gline, (height - gwidth) / 2 - gline, gdepth + gline, gline)
        painter.drawRect(-gdepth - gline, (height - gwidth) / 2, gline, gwidth)
        painter.drawRect(-gdepth - gline, (height + gwidth) / 2, gdepth + gline, gline)

        if self.world.right_goal.is_blue:
            painter.setBrush(BLUE)
            painter.setPen(BLUE)
        else:
            painter.setBrush(YELLOW)
            painter.setPen(YELLOW)
        painter.drawRect(width, (height - gwidth) / 2 - gline, gdepth + gline, gline)
        painter.drawRect(width + gdepth, (height - gwidth) / 2, gline, gwidth)
        painter.drawRect(width, (height + gwidth) / 2, gdepth + gline, gline)

        # Reset transformation
        painter.restore()


class BallView(QGraphicsItem):

    def __init__(self, ball):
        super(BallView, self).__init__()
        self.ball = ball

    @property
    def uuid(self):
        return BALL

    def boundingRect(self):
        radius = s(self.ball.radius)
        return QRectF(-radius, -radius, 2 * radius, 2 * radius)

    def position(self):
        x, y, width, height = s(self.ball.x, self.ball.y, self.ball.world.length, self.ball.world.width)
        self.setPos(x, -y)

    def paint(self, painter, option, widget=None):

        # Save transformation:
        painter.save()

        painter.setBrush(ORANGE)
        painter.setPen(ORANGE)
        radius = s(self.ball.radius)
        painter.drawEllipse(-radius, -radius, 2 * radius, 2 * radius)

        # Reset transformation
        painter.restore()
