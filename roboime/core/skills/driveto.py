# coding: utf-8
from numpy import array
from numpy.linalg import norm

from .goto import Goto
from ...utils.mathutils import cos, sin
from ...utils.geom import Point


class DriveTo(Goto):
    
    angle_kick_min_error = 0.5
    angle_approach_min_error = 15
    angle_tolerance = 10
    orientation_tolerance = 0.7
    distance_tolerance = 0.14
    
    def __init__(self, robot, base_angle=0, base_point=Point([0, 0]), angle=0, threshold=0.005, max_error_d=0.2, max_error_a=10.0, **kwargs):
        """
                                x <-- target (calculated by skill)
                               /
               threshold -->  /    base_angle
                             /\  L´
                            /__|______ (x-axis)
            base_point --> O

        The base is the point from where we calculate a distance in order to find our target.
        The parameters are:

          threshold: distance to keep away from the base point
         base_angle: base angle, direction from base to target point
         base_point: base point, the base coords
            t_angle: target angle, robot facing angle
             target: target point
        max_error_d: limit distance to consider the robot has reached its target
        max_error_a: limit angle distance to consider the robot has reached its target
        """

        super(DriveTo, self).__init__(robot, angle=angle, **kwargs)
        self.should_avoid = False
        self.robot = robot
        self._base_angle = base_angle
        self._base_point = base_point
        self.threshold = threshold
        self.max_error_d = max_error_d
        self.max_error_a = max_error_a

    @property
    def base_angle(self):
        if callable(self._base_angle):
            return self._base_angle()
        else:
            return self._base_angle

    @base_angle.setter
    def base_angle(self, angle):
        self._base_angle = angle

    @property
    def base_point(self):
        if callable(self._base_point):
            return self._base_point()
        else:
            return self._base_point

    @base_point.setter
    def base_point(self, point):
        self._base_point = point

    def _step(self):
        # make numpy arrays out of base_point and threshold with base_angle direction so we can sum them
        p1 = array(self.base_point)
        p2 = array([cos(self.base_angle), sin(self.base_angle)]) * self.threshold

        # sum'em and let Goto do its thing
        self.target = Point(p1 + p2)
        super(DriveTo, self)._step()
    
    def bad_position(self):
        bad_distance = self.robot.kicker.distance(self.ball) > self.distance_tolerance + .01
        #bad_orientation = abs(self.delta_orientation()) >= self.orientation_tolerance + 3
        bad_angle = abs(self.delta_angle()) >= self.angle_tolerance + 5
        return bad_distance or bad_angle

    def good_position(self):
        good_distance = self.robot.kicker.distance(self.ball) <= self.distance_tolerance
        #good_orientation = abs(self.delta_orientation()) < self.orientation_tolerance       
        good_angle = abs(self.delta_angle()) < self.angle_tolerance
        return good_distance and good_angle

    def delta_angle(self):
        delta =  self.robot.angle_to_point(self.ball) - self.ball.angle_to_point(self.lookpoint)
        return (180 + delta) % 360 - 180

    def delta_orientation(self):
        delta =  self.robot.angle - self.ball.angle_to_point(self.lookpoint)
        return (180 + delta) % 360 - 180
    
    def close_enough(self):
        good_distance = self.robot.kicker.distance(self.ball) <= self.distance_tolerance
        #good_orientation = abs(self.delta_orientation()) < self.orientation_tolerance       
        good_angle = abs(self.delta_angle()) < self.angle_tolerance
        return good_distance and good_angle

    #def close_enough(self):
    #    if self.target is None:
    #        return None
    #    error_d = norm(array(self.target) - array(self.robot))
    #    error_a = abs(self.robot.angle - self.angle) % 180.0
    #    error_a = min(error_a, 180. - error_a)
    #    #print error_d, error_a
    #    # We're close enough if both errors are sufficiently small.
    #    return error_d < self.max_error_d and error_a < self.max_error_a
