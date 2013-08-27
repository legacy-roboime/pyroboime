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
        if not 'threshold' in kwargs:
            kwargs['threshold'] = robot.front_cut
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
