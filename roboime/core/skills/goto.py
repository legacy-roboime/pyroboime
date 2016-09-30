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
from numpy import array, linspace
from numpy.linalg import norm

from .. import Skill
from ...utils.geom import Point
from ...utils.pidcontroller import PidController


class Goto(Skill):
    """
    New goto using Stox's path planning
    """
    # path planning
    min_dist = 0.25
    max_recursive = 3
    divisions = 10

    # distance to consider target arrival
    arrive_distance = 1e-3
    max_angle_error = 1.0

    # flag to disable actual implementation
    decoupled = False

    def __init__(self, robot, target=None, angle=None, avoid_collisions=True,
                 deterministic=True, ignore_defense_area=False, deaccel_dist=0.8,
                 **kwargs):
        super(Goto, self).__init__(robot, deterministic=deterministic, **kwargs)
        self.angle_controller = PidController(
            kp=1., ki=.0, kd=.0, integ_max=.5, output_max=360)
        self.norm_controller = PidController(
            kp=.1, ki=0.01, kd=.5, integ_max=50., output_max=1.2)
        self.x_controller = PidController(
            kp=.3, ki=0.01, kd=.05, integ_max=5., output_max=.8)
        self.y_controller = PidController(
            kp=.3, ki=0.01, kd=.05, integ_max=5., output_max=.8)

        self.angle = angle
        self.final_target = target
        self.target = None
        self.avoid_collisions = avoid_collisions
        self.next_target = target
        self.ignore_defense_area = ignore_defense_area
        self.deaccel_dist = deaccel_dist

        self.collision_distance = self.robot.radius * 1.5

    def arrived(self):
        dist = array(self.robot) - array(self.target)
        return norm(dist) <= self.arrive_distance

    def oriented(self):
        angle = (180 + self.angle - self.robot.angle) % 360 - 180
        return abs(angle) <= self.max_angle_error

    def _step(self):
        final = self.final_target if self.ignore_defense_area else self.robot.goal.point_outside_area(self.final_target)
        self.target = self.path_planner(final)

        if self.decoupled:
            a = self.angle or self.robot.angle or 0.0
            self.robot.action.target = (self.target.x, self.target.y, a)
            return

        # angle control using PID controller
        if self.angle is not None and self.robot.angle is not None:
            angle = (180 + self.angle - self.robot.angle) % 360 - 180
            self.angle_controller.input = angle
            self.angle_controller.feedback = 0.0
            self.angle_controller.step()
            va = self.angle_controller.output
        else:
            va = 0.0

        diff_to_final = array(final) - array(self.robot)
        diff = array(self.target) - array(self.robot)
        vel = self.robot.max_speed if norm(diff_to_final) > self.deaccel_dist else self.robot.max_speed * norm(diff)
        v = diff * (vel / norm(diff) if norm(diff) > 0.0 else 0.0)
        self.robot.action.absolute_speeds = v[0], v[1], va

    def path_planner(self, target, depth=0):
        diff = array(target) - array(self.robot)

        if self.avoid_collisions and depth < self.max_recursive and norm(diff) > self.min_dist:

            # TODO: Rewrite the python's way
            points = []
            x = linspace(target.x, self.robot.x, self.divisions)
            y = linspace(target.y, self.robot.y, self.divisions)
            for i in range(self.divisions):
                if self.ignore_defense_area:
                    points.append(Point(x[i], y[i]))
                else:
                    points.append(self.robot.goal.point_outside_area(Point(x[i], y[i])))
            points.pop(0)

            robots = self.get_robots()
            for point in points:
                if self.point_inside_robot(point, robots):
                    # TODO: Rewrite the python's way
                    n = diff * self.collision_distance / norm(diff)
                    temp = Point(-n[1] + point.x, n[0] + point.y)
                    target1 = self.path_planner(temp, depth + 1)
                    diff1 = norm(array(self.final_target) - array(target1))
                    free1 = not self.point_inside_robot(target1, robots)

                    temp = Point(n[1] + point.x, -n[0] + point.y)
                    target2 = self.path_planner(temp, depth + 1)
                    diff2 = norm(array(self.final_target) - array(target2))
                    free2 = not self.point_inside_robot(target2, robots)

                    if free1 and free2:
                        return target1 if diff1 < diff2 else target2
                    else:
                        return target1 if free1 else target2
        return target

    def get_robots(self):
        return [r for r in self.world.robots if r.uid != self.robot.uid]

    def point_inside_robot(self, point, robots):
        for robot in robots:
            if point.distance(robot) <= 4 * self.robot.radius:
                return True
        return False

    @property
    def final_target(self):
        if callable(self._final_target):
            return self._final_target()
        else:
            return self._final_target or self.target

    @final_target.setter
    def final_target(self, target):
        self._final_target = target
