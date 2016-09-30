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
from numpy import sign
from numpy import linspace
from itertools import groupby

from ...utils.mathutils import sin, cos
from ...utils.geom import Line, Point
from .. import Tactic
from ..skills.gotolooking import GotoLooking
from ..tactics.zickler43 import Zickler43


class Goalkeeper(Tactic):
    """
    This is the goalie. Make it smart.

    If you set the aggressive mode on, guess what, it'll get angry
    when the ball is close, and kick it, kick it as far as possible
    whenever possible. Sometimes you may not want that, choose wisely.
    """
    def __init__(self, robot, aggressive=False, angle=0):
        """
        angle: this angle is how much inside the goal the goalkeeper must be
          when 0 it's completely outside, when 90, it's half inside, when 180
          it's completely inside, naturally values greater than 90 don't make
          much sense
        aggressive: this sets the aggressive mode, which means that the
          goalkeeper will also act as an attacker when it is the closer robot
          to the ball
        """

        super(Goalkeeper, self).__init__(robot, deterministic=True)
        self.aggressive = aggressive
        self.goto = GotoLooking(
            robot,
            lookpoint=robot.world.ball,
            target=lambda: robot.goal,
            avoid_collisions=True,
            ignore_defense_area=True,
            deaccel_dist=0.2
        )
        self.chip = Zickler43(robot, always_force=True, always_chip=True,
                              respect_mid_line=False, ignore_defense_area=True)
        self.angle = angle
        # should parametrize these
        # time in seconds to predict future ball position
        self.look_ahead_time = 4.0
        self.domination_radius = 0.135
        self.safety_ratio = 2.0

        self.p1 = Point(
            array(self.goal.p1) + array((self.robot.radius * -sign(self.goal.x), 0))
        )
        self.p2 = Point(
            array(self.goal.p2) + array((self.robot.radius * -sign(self.goal.x), 0))
        )

        # Aaaand the home line
        self.home_line = Line(self.p1, self.p2)

    def _step(self):

        self.goto.final_target = self.home_line.centroid

        # TODO: if ball is inside area and is slow, kick/pass it far far away

        # Build the home line
        #
        #   ,-> goal
        # +-o
        # |   | <- home_line
        # |   |
        # |   |
        # +-o/_ <- angle
        #

        if self.aggressive:
            if self.robot is self.world.closest_robot_to_ball():
                return self.chip.step()

        # watch the enemy
        # TODO: get the chain of badguys, (badguy and who can it pass to)

        # if the badguy has closest reach to the ball then watch it's orientation
        danger_bot = self.world.closest_robot_to_ball(color=self.team.enemy_team.color)

        # If dangerBot is an enemy, we shall watch his orientation. If he's a
        # friend, we move on to a more appropriate strategy
        if danger_bot is not None:  # and danger_bot.distance(self.ball) < self.domination_radius:
            # Line starting from the dangerBot spanning twice the width of the
            # field (just to be sure) to the goal with the desired orientation.
            future_point = Point(
                array(danger_bot) + array((cos(danger_bot.angle),
                                           sin(danger_bot.angle))) * 2 * self.world.width
            )
            danger_line = Line(danger_bot, future_point)

            if danger_line.crosses(self.goal.line):
                point_to_go = danger_line.intersection(self.goal.line)
                if point_to_go.geom_type == 'Point':
                    self.goto.final_target = self.goal_to_home(point_to_go)
                else:
                    pass
            else:
                pass

        future_ball = array(self.ball) + self.ball.speed * self.look_ahead_time
        ball_now, ball_then = Point(self.ball), Point(future_ball)
        ball_line = Line(ball_now, ball_then)

        if ball_now.equals(ball_then) and ball_line.crosses(self.goal.line):
            point_to_go = ball_line.intersection(self.goal.line)

            if point_to_go.geom_type == 'Point':
                self.goto.final_target = self.goal_to_home(point_to_go)
            else:
                pass

        # If the ball is in defense area, the goalkeeper must shoot
        if self.ball.within(self.goal.area):
            return self.chip.step()

        self.goto.step()

    def point_to_defend(self):
        """
        This method comes from Zickler.

        The main difference is that it transfers the point to defend from the
        goal line to the base line.
        """
        our_goal = self.team.goal
        max_hole = []

        possible_points = [(y, self.world.has_clear_shot(Point(our_goal.x, y))) for y in linspace(our_goal.p2.y, our_goal.p1.y, 10)]

        for has_clear_shot, group in groupby(possible_points, lambda point_has: point_has[1]):
            if has_clear_shot:
                hole = list(group)
                if len(hole) > len(max_hole):
                    max_hole = hole

        if len(max_hole) != 0:
            y = (max_hole[0][0] + max_hole[-1][0]) / 2
            return Point(
                our_goal.x - sign(our_goal.x) * self.robot.radius,
                y
                # XXX: no reason for this
                # (our_goal.x - sign(our_goal.x) * self.robot.radius) * y / our_goal.x
            )

    def goal_to_home(self, point):
        return Point(array(point) + array((self.robot.radius * -sign(self.goal.x), 0)))
