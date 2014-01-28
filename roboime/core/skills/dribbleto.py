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
from numpy import pi, sign, array
from numpy.linalg import norm

from ...utils.mathutils import sqrt
from ...utils.pidcontroller import PidController
from .. import Skill


class DribbleTo(Skill):
    """
    TODO: extract the orientation stuff so that it becomes reusable.
    """

    angle_error_tolerance = 0.5
    angle_tolerance = 0.5
    distance_tolerance = 0.3

    def __init__(self, robot, target=None, lookpoint=None, angle=None, **kwargs):
        super(DribbleTo, self).__init__(robot, deterministic=True, **kwargs)
        self.target = target
        self.angle = angle
        self.lookpoint = lookpoint
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
        # it has to dribble!
        self.robot.action.dribble = 1.0
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

        z = 0.0
        if abs(delta_angle) < self.angle_error_tolerance:
            z = self.robot.max_speed_dribbling / 6
            v = w = 0

        # action!
        self.robot.action.speeds = (z, v, -w)
