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
from numpy import linspace, array
from itertools import groupby

from .. import Tactic
from ...utils.statemachine import Transition
from ..skills.drivetoball import DriveToBall
#from ..skills.sampledkick import SampledKick
from ..skills.kickto import KickTo
from ..skills.sampleddribble import SampledDribble
from ..skills.halt import Halt
from ...utils.geom import Point
from ...base import Rules


class Zickler43(Tactic):
    """
    For more details see page 43 of the Zickler thesis.

    Ok, actually, no. This tactic is far from the original however
    the purpose is basically the same. This is an attacker. Main
    differences from zickler thesis are that this tactic is deterministic,
    and that the minikick skill doesn't appear here.

    Somebody has to make goals, so, this is it, this will be
    the tactic that will make goals. And it will!
    """

    conduction_tolerance = 0.6

    def __init__(self, robot, deterministic=True):
        self._lookpoint = self.point_to_kick
        self._robot = robot
        self.drive = DriveToBall(robot, name='Get the Ball', lookpoint=self.robot.enemy_goal, deterministic=True, avoid_collisions=True)
        self.dribble = SampledDribble(robot, name='Drag the Ball', deterministic=deterministic, lookpoint=lambda: self.lookpoint, minpower=0.0, maxpower=1.0)
        self.goal_kick = KickTo(robot, name='KICK IT!!!', lookpoint=lambda: self.lookpoint, minpower=0.9, maxpower=1.0)
        self.force_kick = KickTo(robot, name='FUCKING KICK IT ALREADY!!!', force_kick=True, lookpoint=lambda: self.lookpoint, minpower=0.9, maxpower=1.0)
        self.wait = Halt(robot)
        self.stored_point = None
        self.time_of_last_kick = 0

        super(Zickler43, self).__init__(robot, deterministic=deterministic, initial_state=self.drive, transitions=[
            #Transition(self.drive, self.dribble, condition=lambda: self.drive.close_enough()),
            Transition(self.drive, self.dribble, condition=lambda: self.drive.close_enough(), callback=self.store_point),
            Transition(self.dribble, self.drive, condition=lambda: not self.dribble.close_enough(), callback=self.clear_point),
            Transition(self.dribble, self.goal_kick, condition=lambda: self.dribble.close_enough()),
            Transition(self.dribble, self.force_kick, condition=lambda: self.stored_point.distance(self.robot) > self.conduction_tolerance * Rules.max_conduction_distance, callback=self.clear_point),
            #Transition(self.goal_kick, self.drive, condition=lambda: not self.goal_kick.close_enough()),
            Transition(self.goal_kick, self.drive, condition=lambda: self.goal_kick.bad_position(), callback=lambda: map(lambda a: a(), [self.clear_point, self.set_time])),
            Transition(self.goal_kick, self.force_kick, condition=lambda: self.stored_point.distance(self.robot) > self.conduction_tolerance * Rules.max_conduction_distance, callback=self.clear_point),
            Transition(self.force_kick, self.drive, condition=lambda: self.goal_kick.bad_position(), callback=lambda: map(lambda a: a(), [self.clear_point, self.set_time])),
        ])

        self.max_hole_size = -1

    def set_time(self):
        self.time_of_last_kick = self.world.timestamp

    def store_point(self):
        self.stored_point = Point(array(self.robot))

    def clear_point(self):
        self.stored_point = None

    @property
    def lookpoint(self):
        if callable(self._lookpoint):
            return self._lookpoint() or self.robot.enemy_goal
        else:
            return self._lookpoint or self.robot.enemy_goal

    @lookpoint.setter
    def lookpoint(self, point):
        self._lookpoint = point

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
