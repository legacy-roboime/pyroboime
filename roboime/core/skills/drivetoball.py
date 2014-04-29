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
from numpy import remainder

from .drivetoobject import DriveToObject


class DriveToBall(DriveToObject):
    """
    This skill is a DriveToObject except that the object is the ball
    and that some parameters are optimized for getting on the ball.
    """

    #enter_angle = 30.0
    enter_angle = 10.0
    exit_angle = 20.0

    def __init__(self, robot, **kwargs):
        # TODO: magic parameters
        super(DriveToBall, self).__init__(robot, point=robot.world.ball, **kwargs)
        self.avoid = robot.world.ball

    def _step(self):
        #if self.target is not None and self.lookpoint is not None:
        #    base_angle = self.target.angle_to_point(self.ball)
        #    robot_angle = self.robot.angle_to_point(self.ball)
        #    delta = remainder(robot_angle - base_angle, 360)
        #    delta = min(abs(delta), abs(delta - 360))
        #    if delta >= self.exit_angle:
        #       self.should_avoid = True

        #    if self.should_avoid:
        #        if delta <= self.enter_angle:
        #            self.should_avoid = False
        super(DriveToBall, self)._step()
