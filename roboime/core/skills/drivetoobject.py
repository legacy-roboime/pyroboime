from .driveto import DriveTo

from ...utils.mathutils import pi
from ...utils.sampler import Sampler


class DriveToObject (DriveTo):
    def __init__(self, robot, object, radius_obj, lookpoint, max_error_d=100, max_error_a=10*pi/180, max_ang_var=15, deterministic=False):
        # There's no such cut: self.threshold = robot.cut+self.radius_obj
        self.threshold = self.radius_obj
        super(DriveToObject, self).__init__(robot, threshold, deterministic)
        self.robot = robot
        self.object = object
        self.radius_obj = radius_obj
        self.lookpoint = lookpoint
        self.max_error_d = max_error_d
        self.max_error_a = max_error_a
        self.deterministic = deterministic
    
    def step(self):
        """
        Robot is positioned oposed to the lookpoint. 
        lookPoint, object and robot stay aligned (and on this exact order)
        e.g.:    object: ball,
              lookpoint: goal,
                  robot: robot
        """
        
        # TODO: check if it allows changes to the original lookpoint (we do not want it!)
        lp = self.lookpoint
        obj = self.object
        
        # target_angle: angle from object to lp (relative to the x axis)
        target_angle = obj.angle(lp)
        
        # TODO: non-deterministic cases
        if not (deterministic):
            angle = max_ang_var
            #if(Sampler.rand_float() > 0.5): #target.setAngle(target_angle + Sampler.rand_float() * angle)
            #else:                           #target.setAngle(target_angle - Sampler.rand_float() * angle)
        
        super(DriveToObject, self).b_point = object
        super(DriveToObject, self).b_angle = 180 + target_angle
        super(DriveToObject, self).t_angle = target_angle
        super(DriveToObject, self).step()
    
    def busy(self):
        return super(DriveToObject, self).busy()