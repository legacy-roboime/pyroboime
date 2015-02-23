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
from numpy import pi, sign, array
from numpy.linalg import norm

#from ...utils.mathutils import sqrt
from ...utils.pidcontroller import PidController
from .. import Skill


class OrientTo(Skill):
    """
    This skill will orient the robot arount a given point to look to another given point,
    """

    angle_tolerance = 0.5
    distance_tolerance = 0.11
    walkspeed = 0.1

    def __init__(self, robot, lookpoint=None, minpower=0.0, maxpower=1.0, **kwargs):
        """
        """
        super(OrientTo, self).__init__(robot, deterministic=True, **kwargs)
        self.lookpoint = lookpoint
        self.minpower = minpower
        self.maxpower = maxpower
        self.angle_controller = PidController(kp=1.8, ki=0, kd=0, integ_max=687.55, output_max=360)
        self.distance_controller = PidController(kp=1.8, ki=0, kd=0, integ_max=687.55, output_max=360)

    @property
    def final_target(self):
        return self.lookpoint

    def good_position(self):
        good_distance = self.robot.kicker.distance(self.ball) <= self.distance_tolerance
        good_angle = abs(self.delta_angle()) < self.angle_tolerance
        return good_distance and good_angle

    def delta_angle(self):
        delta =  self.robot.angle - self.ball.angle_to_point(self.lookpoint)
        return (180 + delta) % 360 - 180

    def _step(self):
        delta_angle = self.delta_angle()

        self.angle_controller.input = delta_angle
        self.angle_controller.feedback = 0.0
        self.angle_controller.step()

        #d = self.robot.front_cut + self.ball.radius
        d = norm(array(self.robot) - array(self.ball))
        r = self.robot.radius

        w = self.angle_controller.output
        max_w = 180.0 * self.robot.max_speed / r / pi
        if abs(w) > max_w:
            w = sign(w) * max_w
        v = pi * w * d / 180.0

        self.robot.action.speeds = (0.0, v, -w)
