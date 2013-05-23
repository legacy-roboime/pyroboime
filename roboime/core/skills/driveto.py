# coding: utf-8
from numpy import array
from numpy.linalg import norm

from .goto import Goto
from ...utils.mathutils import cos, sin
from ...utils.geom import Point


class DriveTo(Goto):
    def __init__(self, robot, b_angle=0, b_point=Point([0, 0]), angle=0, threshold=0.005, max_error_d=0.1, max_error_a=10.0):
        """
                         x <-- target (calculeted by skill)
                        /
        threshold -->  /    b_angle
                      /\  L´
                     /__|______ (x-axis)
        b_point --> O

        The base is the point from where we calculate a distance in order to find our target.
        The parameters are:

          threshold: distance to keep away from the base point
            b_angle: base angle, direction from base to target point
            b_point: base point, the base coords
            t_angle: target angle, robot facing angle
             target: target point
        max_error_d: limit distance to consider the robot has reached its target
        max_error_a: limit angle distance to consider the robot has reached its target
        """

        super(DriveTo, self).__init__(robot, angle=angle)
        self.robot = robot
        self.b_angle = b_angle
        self.b_point = b_point
        self.threshold = threshold
        self.max_error_d = max_error_d
        self.max_error_a = max_error_a

    def step(self):
        # make numpy arrays out of b_point and threshold with b_angle direction so we can sum them
        p1 = array(self.b_point)
        p2 = array([cos(self.b_angle), sin(self.b_angle)]) * self.threshold

        # sum'em and let DriveTo do its thing
        self.target = Point(p1 + p2)
        super(DriveTo, self).step()

    def busy(self):
        if self.target is None:
            return False

        error_d = norm(array(self.target) - array(self.robot))
        error_a = abs(self.robot.angle - self.angle) % 180.0

        # where busy while where not inside the safe zone
        return not (error_d < self.max_error_d and error_a < self.max_error_a)
