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
from numpy.random import random

from .drivetoball import DriveToBall


class SampledDribble(DriveToBall):
    """
    This is a DriveToBall extension that gets the robot
    really close to the ball and make it dribble.
    """

    avoid_collisions = False

    def __init__(self, robot, minpower=0.0, maxpower=1.0, **kwargs):
        """
        minpower and maxpower are in respect to the dribbling power, however
        currently both simulated and real implementations are binary and do not
        yet support variable dribbling speed, it's either max or zero.

        All other options from DriveToBall apply here.
        """
        super(SampledDribble, self).__init__(robot, **kwargs)
        self.minpower = minpower
        self.maxpower = maxpower

    def _step(self):
        # put some dribbling in action
        if self.deterministic:
            self.robot.action.dribble = self.maxpower
        else:
            self.robot.action.dribble = (self.maxpower - self.minpower) * random() + self.minpower

        # temporarily decrease the threshold, does it has to be temporary?
        _threshold, self.threshold = self.threshold, 0.001
        # let DriveToBall do its thing
        super(SampledDribble, self)._step()
        # and restore the threshold
        self.threshold = _threshold
