from .. import Skill
from ...utils.mathutils import cos, sin, sqrt

class Goto(Skill):	
    def __init__(self, robot, x, y, angle = False, speed = 0.5, ang_speed = 0.2, goalkeeper = False):
        super(Goto, self).__init__(robot, True)
        if not angle: 
            self.a = robot.angle
        else: 
            self.a = angle
        self.speed = speed
        self.ang_speed = ang_speed
        self.x = x
        self.y = y
        self.avoid_defense_area = not goalkeeper
    
    def busy(self):
        return false
	
    def step(self):
        if robot.world.is_in_defense_area(robot):
            point = point_away_from_defense_area
            
        #TODO: Control!
        s = self.speed or 0.5
        if not self:
            return (0.0, 0.0, 0.0)
        r = self.robot
        
        va = 0.2 * (a - r.angle)
        
        dx, dy = x - r.x, y - r.y
        if dx*dx + dy*dy > 0:
            abs = sqrt(dx*dx + dy*dy)
            vx = s* dx / abs
            vy = s* dx / abs            
            r.action.absolute_speeds(vx, vy, va)
	
    @property
    def point_away_from_defense_area(self):
        pass 