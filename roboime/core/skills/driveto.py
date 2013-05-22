from numpy import array
from numpy.linalg import norm

from .goto import Goto
from ...utils.mathutils import pi
from ...utils.mathutils import cos, sin
from ...utils.statemachine import Machine
from ...utils.geom import Line
from ...utils.geom import Point


class DriveTo(Goto):
    def __init__(self, robot, b_angle=0, b_point=Point([0, 0]), t_angle=0, threshold=0.5, max_error_d=100, max_error_a=10*pi/180):
        """
              + Target
             /
            /
           /\  b_angle
          /__|______
         O b_point (e.g.: Ball)
         
         base is the point from where we calculate a distance in order to find our target.
         threshold: distance to keep away from the base point
         b_angle: base angle, direction from base to target point
         b_point: base point, the base coords
         t_angle: target angle, robot facing angle
         target: target point
        """
        
        super(DriveTo, self).__init__(robot, angle=t_angle)
        self.robot = robot
        self.b_angle = 180 + b_angle
        self.b_point = b_point
        self.t_angle = t_angle
        self.threshold = threshold
        self.max_error_d = max_error_d
        self.max_error_a = max_error_a
        # ignoreBrake = False
        # boolean that indicates that we're dealing with a deterministic skill:
        # super(DriveTo, self). super(Goto, self).__init__(robot, deterministic=True)
    
    def step(self):
        r = self.robot
        b_a = self.b_angle
        b_p = self.b_point
        thr = self.threshold
        
        b_1 = array(b_p)
        # b_2: direction base -> target
        b_2 = array([ cos(b_a), sin(b_a)]) * thr
        self.target = Point(b_1 - b_2)
        
        print "norma de b_2: ", norm(b_2), "  target: ", self.target, b_1
        
        super(DriveTo, self).step()
    
    def busy(self):
        r = self.robot
        t = self.target
        t_a = self.t_angle
        
        error_d = norm(array(t) - array(r))
        error_a = abs(r.angle - t_a)
        
        if(error_a > pi):
            error_a = 2 * pi - error_a
        
        if(error_d < max_error_d and error_a < max_error_a):
            return False
        else:
            return True