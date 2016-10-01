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
from numpy import array

from .. import Tactic
from ...utils.geom import Point
from ..skills.gotolooking import GotoLooking

from ...utils.mathutils import sin
from ...utils.mathutils import cos


class Blocker(Tactic):
    """
    Follow a point, maintaining a fixed distance from it while
    covering another point. Pretty much like a follow and cover.
    """
    # TODO
    def __init__(self, robot, arc, distance=0.59, blockpoint=None):
        """
        arc: angle deviation in relation to line from robot to goal
        distance: constant distance to keep from blockpoint
        blockpoint: point to block, if none falls back to ball
        """
        super(Blocker, self).__init__(robot, deterministic=True)
        # TODO: implement with follow and cover somehow, needs angle deviantion
        self.blockpoint = self.ball if blockpoint is None else blockpoint
        self.goto = GotoLooking(
            self.robot,
            name='Block!',
            lookpoint=lambda: self.blockpoint
        )
        self.arc = arc
        self.dist = distance

    def point_for_arc(self, arc):
        base_angle = self.ball.angle_to_point(self.goal)
        return Point(
            array((self.dist * cos(base_angle + arc),
                   self.dist * sin(base_angle + arc))) + array(self.blockpoint)
        )

    def dist_to_arc(self, arc):
        return self.robot.distance(self.point_for_arc(arc))

    @property
    def point_to_cover(self):
        return self.point_for_arc(self.arc)

    def _step(self):
        self.goto.target = self.point_to_cover
        self.goto.step()
