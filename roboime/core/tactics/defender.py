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
from ...utils.statemachine import Transition
from ..skills.followandcover import FollowAndCover
from ...utils.geom import Point
from ..skills.gotolooking import GotoLooking

from ...utils.mathutils import sin
from ...utils.mathutils import cos


class Defender(Tactic):
    """
    If you need robots on the defense line, use this.

    Also one may want a closer body-to-body defense, in that
    case you may set an enemy.

    Remember that you may not only defend the goal, you're allowed
    to defend any point on the field.
    """
    def __init__(self, robot, enemy, cover=None, distance=None, follow_distance=0.3, proximity=1.5, flapping_margin=0.1, arc=0.0):
        """
        cover: point or object to cover
        distance: distance to keep from the cover point
        follow_distance: distance to keep from the enemy when following it
        proximity: distance to switch from covering mode to following mode
        flapping_margin: distance margin to avoid flapping between covering and following
        """
        self._robot = robot
        self.proximity = proximity
        self.cover = robot.goal if cover is None else cover
        self.distance = distance if distance is not None else self.world.defense_radius + self.world.defense_stretch / 2 + 0.10
        self.follow_distance = follow_distance
        self.proximity = proximity
        self.flapping_margin = flapping_margin
        self._enemy = enemy
        self.arc = arc
        self.follow_and_cover = FollowAndCover(
            robot,
            name='Get the enemy!',
            follow=self.enemy,
            cover=self.cover,
            distance=self.follow_distance,
            referential=self.enemy,
        )
        self.goto = GotoLooking(
            robot,
            name='Defend!',
            lookpoint=self.enemy
        )
        # the following line is so that lambdas can use self.robot instead of
        # robot and keep track of the robot
        # even if it changes, although tactics are supposed to never change its
        # robot we're trying to keep it flexible
        super(Defender, self).__init__(
            robot,
            deterministic=True,
            initial_state=self.goto,
            transitions=[
                Transition(
                    self.goto,
                    self.follow_and_cover,
                    condition=lambda: self.enemy.distance(self.cover) <
                    self.proximity - self.flapping_margin and
                    not self.world.defense_area(self.robot.color).contains(self.ball)
                ),
                Transition(
                    self.follow_and_cover,
                    self.goto,
                    condition=lambda: self.enemy.distance(self.cover) >
                    self.proximity + self.flapping_margin or
                    self.world.defense_area(self.robot.color).contains(self.ball)
                ),
            ]
        )

    def _step(self):
        base_angle = self.cover.angle_to_point(self.enemy)
        self.goto.target = Point(
            array((self.distance * cos(base_angle + self.arc),
                   self.distance * sin(base_angle + self.arc))) + array(self.cover)
        )
        super(Defender, self)._step()

    @property
    def enemy(self):
        return self._enemy

    @enemy.setter
    def enemy(self, new_enemy):
        self._enemy = new_enemy
        self.follow_and_cover.follow = new_enemy
        self.follow_and_cover.referential = new_enemy
        self.goto.lookpoint = new_enemy
