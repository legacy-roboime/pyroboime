from numpy.random import random

from ...utils.mathutils import sqrt
from .drivetoball import DriveToBall


KICKPOWER = 5.0
#KICKPOWER = 1.0 # check this value...


def kick_power(distance, initial_speed=0.0, final_speed=0.0):
    mi = 0.4
    g = 9.81
    a = mi * g
    return abs(initial_speed * final_speed + 2 * a * distance) / sqrt(KICKPOWER)


class SampledKick(DriveToBall):
    """
    This class is a DriveToBall extension that will get the robot
    close to the ball and kick it with enough power to reach a
    given distance with a given speed, that means, arrive at that
    distance with that speed.

    The equation to calculate inital speed is not perfect and may
    need calibration, however one may choose to use the max speed
    instead for most goals.
    """
    def __init__(self, robot, receiver=None, minpower=0.0, maxpower=1.0, **kwargs):
        """
        minpower and maxpower are in respect to the kicking power.
        receiver must be a point like, if specified the kick will have
        it's power calculated in a manner to arrive with speed zero at that point.

        All other options from DriveToBall apply here.
        """
        super(SampledKick, self).__init__(robot, **kwargs)
        self.receiver = receiver
        self.minpower = minpower
        self.maxpower = maxpower

    def step(self):
        if not self.busy():
            # put some kicking in action
            if self.receiver is not None:
                power = kick_power(self.ball.distance(self.receiver))
            else:
                if self.deterministic:
                    power = self.maxpower
                else:
                    power = (self.maxpower - self.minpower) * random() + self.minpower
            self.robot.action.kick = power

        # do some pre-dribbling, should we do it?
        self.robot.action.dribble = 0.5

        # temporarily decrease the threshold, does it has to be temporary?
        _threshold, self.threshold = self.threshold, 0.05
        # let DriveToBall do its thing
        super(SampledKick, self).step()
        # and restore the threshold
        self.threshold = _threshold
