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


class ChipKickTo(Skill):
    """
    This class is an alternative to SampledKick.
    Meanwhile it's experimental, depending on the results it'll stay or not.
    """
    angle_error_tolerance = 0.5
    angle_tolerance = 0.5
    distance_tolerance = 0.11
    walkspeed = 0.1

    def __init__(self, robot, lookpoint=None, minpower=0.0, maxpower=1.0, **kwargs):
        """
        """
        super(ChipKickTo, self).__init__(robot, deterministic=True, **kwargs)
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
        #print 'blasdbflas'
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
            kp = kick_power(self.lookpoint.distance(self.robot))
            kp = min(max(kp, self.minpower), self.maxpower)
            self.robot.action.chipkick = kp
            z = self.walkspeed
        else:
            self.robot.action.dribble = 1.0

        self.robot.action.speeds = (z, v, -w)
