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
from numpy import linspace
from itertools import groupby

from .. import Tactic
from ...utils.statemachine import Transition
from ..skills.drivetoball import DriveToBall
from ..skills.sampledkick import SampledKick
from ..skills.sampleddribble import SampledDribble
from ..skills.halt import Halt
from ...utils.geom import Point
from ..skills.gotolooking import GotoLooking


class ReceivePassAndKick(Tactic):
    '''
    This tactic has the objective of receiving the ball from
    another robot while aiming for the goal.

    This tactic is designed to work along a ExecutePass tactic
    (or any other tactic that implements its methods). This is
    so that one tactic can signal to the other when it is ready,
    while obscuring details such as which robot is doing what.
    '''

    class CompanionCube(object):
        def __init__(self, robot):
            self._robot = None

        @property
        def robot(self):
            return self._robot

        @property
        def ready(self):
            return True

    def __init__(self, robot, point=None, companion=None, deterministic=True):
        self._robot = robot
        self._point = point or self.robot
        self.companion = companion or self.CompanionCube(self.robot)

        self.goto = GotoLooking(self.robot, target=self._point, lookpoint=lambda: self.point_to_kick())
        super(ReceivePassAndKick, self).__init__(robot, deterministic, initial_state=self.goto, transitions=[])

    def _step(self):
        self.robot.action.kick = 1.
        super(ReceivePassAndKick, self)._step()

    @property
    def point(self):
        if callable(self._point):
            return self._point()
        else:
            return self._point or Point(0, 0)

    @point.setter
    def point(self, point):
        self._point = point

    def ready(self):
        return self.robot.distance(self.point) < 0.2

    def point_to_kick(self):
        enemy_goal = self.robot.enemy_goal
        max_hole = []

        possible_points = [(y, self.world.has_clear_shot(Point(enemy_goal.x, y))) for y in linspace(enemy_goal.p2.y, enemy_goal.p1.y, 5)]

        for has_clear_shot, group in groupby(possible_points, lambda (point, has): has):
            if has_clear_shot:
                hole = list(group)
                if len(hole) > len(max_hole):
                    max_hole = hole

        if len(max_hole) != 0:
            y = (max_hole[0][0] + max_hole[-1][0]) / 2
            return Point(enemy_goal.x, y)
        else:
            return Point(enemy_goal.x, enemy_goal.y)
