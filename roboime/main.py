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
import logging
from sys import stdout
from math import degrees, radians

from numpy import array

from .base import World, Referee
from .core.plays import autoretaliate
from .core.plays import obeyreferee


logger = logging.getLogger(__name__)


class Main(object):
    """
    This is a simple example with no graphical interface.
    """

    def init(self):
        logger.debug('started')

        # Version check I/O
        magic_string, version = input().split()
        if magic_string == 'ROBOIME_AI_PROTOCOL' and int(version) == 1:
            print('COMPATIBLE 1')
        else:
            print('NOT_COMPATIBLE 1')
            exit(0)
        stdout.flush()

        logger.debug('compatible')

        # Geometry input
        i = iter(input().split())
        World.length = float(next(i))
        World.width = float(next(i))
        World.goal_width = float(next(i))
        World.center_radius = float(next(i))
        World.defense_radius = float(next(i))
        World.defense_stretch = float(next(i))
        self.world = World()
        self.world.inited = True
        self.play = autoretaliate.AutoRetaliate(self.world.left_team)
        self.play = obeyreferee.ObeyReferee(self.play)

        logger.debug('initialized')

    def step(self):
        ids = []

        # Input
        i = iter(input().split())
        counter = int(next(i))
        self.world.timestamp = float(next(i))
        referee = self.world.referee
        referee.state = Referee.State(next(i))
        more_info = next(i)
        if referee.state == Referee.State.avoid:
            referee.more_info = int(more_info)
        referee.score_player = int(next(i))
        referee.score_opponent = int(next(i))
        referee.goalie_id_player = int(next(i))
        referee.goalie_id_opponent = int(next(i))

        ball_x, ball_y, ball_vx, ball_vy = map(float, input().split())
        self.world.ball.update(ball_x, ball_y)
        self.world.ball.speed = array((ball_vx, ball_vy))

        for robot in self.world.robots:
            robot.active = False

        robot_count_player = int(input())
        for _ in range(robot_count_player):
            robot_id, robot_x, robot_y, robot_w, robot_vx, robot_vy, robot_vw = map(float, input().split())
            robot_id = int(robot_id)
            ids.append(robot_id)
            robot = self.world.left_team[robot_id]
            robot.active = True
            robot.update(robot_x, robot_y)
            robot.angle = degrees(robot_w)
            robot.speed = array((robot_vx, robot_vy, robot_vw))

        robot_count_opponent = int(input())
        for _ in range(robot_count_opponent):
            robot_id, robot_x, robot_y, robot_w, robot_vx, robot_vy, robot_vw = map(float, input().split())
            robot_id = int(robot_id)
            robot = self.world.right_team[robot_id]
            robot.active = True
            robot.update(robot_x, robot_y)
            robot.angle = degrees(robot_w)
            robot.speed = array((robot_vx, robot_vy, degrees(robot_vw)))

        # Actual AI
        self.play.step()

        # Output
        print(counter)

        for robot_id in ids:
            robot = self.world.left_team[robot_id]
            action = robot.action
            v_tangent, v_normal, v_angular = action.speeds
            v_angular = radians(v_angular)
            kick_force = min(action.kick or 0.0, 1.0) * 6.0
            chip_force = min(action.chipkick if action.chipkick and not action.kick else 0.0, 1.0) * 6.0
            dribble = 1 if action.dribble and not (action.kick or action.chipkick) else 0
            print(v_tangent, v_normal, v_angular, kick_force, chip_force, dribble)

        stdout.flush()

    def mainloop(self):
        try:
            self.init()
            while True:
                self.step()
        except KeyboardInterrupt:
            pass
