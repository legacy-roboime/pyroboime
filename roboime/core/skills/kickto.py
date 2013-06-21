from numpy import pi, sign, array
from numpy.linalg import norm

from ...utils.mathutils import sqrt
from ...utils.pidcontroller import PidController
from .. import Skill


KICKPOWER = 5.0
#KICKPOWER = 1.0 # check this value...


def kick_power(distance, initial_speed=0.0, final_speed=0.0):
    mi = 0.4
    g = 9.81
    a = mi * g
    return abs(initial_speed * final_speed + 2 * a * distance) / sqrt(KICKPOWER)


class KickTo(Skill):
    """
    This class is an alternative to SampledKick.
    Meanwhile it's experimental, depending on the results it'll stay or not.
    """
    tolerance = 2.0

    def __init__(self, robot, lookpoint=None, minpower=0.0, maxpower=1.0, **kwargs):
        """
        """
        super(KickTo, self).__init__(robot, deterministic=True, **kwargs)
        self.lookpoint = lookpoint
        self.minpower = minpower
        self.maxpower = maxpower
        self.angle_controller = PidController(kp=1.8, ki=0, kd=0, integ_max=687.55, output_max=360)
        self.distance_controller = PidController(kp=1.8, ki=0, kd=0, integ_max=687.55, output_max=360)

    def _step(self):
        self.robot.action.dribble = 1.0

        delta_angle =  self.robot.angle - self.ball.angle_to_point(self.lookpoint)

        self.angle_controller.input = (180 + delta_angle) % 360 - 180
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

        if abs(delta_angle) < self.tolerance:
            self.robot.action.kick = kick_power(self.lookpoint.distance(self.robot))
            self.robot.action.dribble = None
            z = 0.03

        #print (w * d, 0.0, w)
        self.robot.action.speeds = (z, v, -w)
