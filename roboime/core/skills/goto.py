from .. import Skill
#from ...utils.mathutils import cos, sin, sqrt
from ...utils.mathutils import sqrt


class Goto(Skill):
    def __init__(self, robot, x, y, angle=False, speed=0.5, ang_speed=0.2, goalkeeper=False):
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
        return False

    def step(self):
        #if self.world.is_in_defense_area(robot):
        #    point = point_away_from_defense_area

        #TODO: Control!
        s = self.speed or 0.5
        if not self:
            return (0.0, 0.0, 0.0)
        r = self.robot

        va = 0.2 * (self.a - r.angle)

        dx, dy = self.x - r.x, self.y - r.y
        if dx * dx + dy * dy > 0:
            absol = sqrt(dx * dx + dy * dy)
            vx = s * dx / absol
            vy = s * dx / absol
            r.action.absolute_speeds(vx, vy, va)

    @property
    def point_away_from_defense_area(self):
        pass
