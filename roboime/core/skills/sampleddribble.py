from numpy.random import random

from .drivetoball import DriveToBall


class SampledDribble(DriveToBall):
    """
    This is a DriveToBall extension that gets the robot
    really close to the ball and make it dribble.
    """
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

    def step(self):
        # put some dribbling in action
        if self.deterministic:
            self.robot.action.dribble = self.maxpower
        else:
            self.robot.action.dribble = (self.maxpower - self.minpower) * random() + self.minpower

        # temporarily decrease the threshold, does it has to be temporary?
        _threshold, self.threshold = self.threshold, 0.001
        # let DriveToBall do its thing
        super(SampledDribble, self).step()
        # and restore the threshold
        self.threshold = _threshold
