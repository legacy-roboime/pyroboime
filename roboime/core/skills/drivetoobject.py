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
from numpy.random import random
from numpy import remainder

from .driveto import DriveTo
from .gotoavoid import GotoAvoid


class DriveToObject(DriveTo, GotoAvoid):
    def __init__(self, robot, point, lookpoint, **kwargs):
        """
        Robot is positioned oposed to the lookpoint.
        lookPoint, object and robot stay aligned (and on this exact order)
        e.g.:     point: ball
              lookpoint: goal
                  robot: robot

        In adition to those, checkout DriveTo parameters as they are also
        valid for this skill, EXCEPT for base_point, which is mapped to point.
        """
        if 'threshold' not in kwargs:
            kwargs['threshold'] = robot.radius * 1.1
        super(DriveToObject, self).__init__(robot, base_point=point, **kwargs)
        self._lookpoint = lookpoint

    @property
    def lookpoint(self):
        if callable(self._lookpoint):
            return self._lookpoint()
        else:
            return self._lookpoint

    @lookpoint.setter
    def lookpoint(self, point):
        self._lookpoint = point

    def _step(self):
        # the angle from the object to the lookpoint, thanks to shapely is this
        # that's the angle we want to be at
        self.angle = self.base_point.angle_to_point(self.lookpoint)

        # nondeterministically we should add a random spice to our
        # target angle, of course, within the limits of max_ang_var
        if not self.deterministic:
            self.angle += self.max_ang_var * (0.5 - random())

        # ultimately we should update our base angle to the oposite
        # of our target angle and let drive to object to its thing
        if self.angle is not None:
            self.base_angle = remainder(self.angle + 180, 360)
        super(DriveToObject, self)._step()
