from numpy import array
from numpy.linalg import norm

from .. import Skill
#from ...utils.mathutils import cos, sin, sqrt
from ...utils.mathutils import sqrt
from ...utils.mathutils import exp
from ...utils.geom import Point
from ...utils.pidcontroller import PidController
#import sys


class Goto(Skill):
    def __init__(self, robot, target=None, angle=None):
        super(Goto, self).__init__(robot, deterministic=True)
        #TODO: find the right parameters
        self.angle_controller = PidController(kp=1.8, ki=0, kd=0, integ_max=687.55, output_max=360)
        #self.angle_controller = PidController(kp=1.324, ki=0, kd=0, integ_max=6.55, output_max=1000)
        self.angle = angle if angle is not None else robot.angle
        self.target = target if target is not None else robot

    def busy(self):
        return False

    def step(self):
        r = self.robot

        # check wether the point we want to go to will make the robot be in the defense area
        # if so then we'll go to the nearest point that meets that constraint
        if not r.is_goalkeeper and r.world.is_in_defense_area(body=self.target.buffer(r.radius), color=r.color):
            self.target = self.point_away_from_defense_area

        self.angle_controller.input = (180 + self.angle - self.robot.angle) % 360 - 180

        self.angle_controller.feedback = 0.0
        self.angle_controller.step()
        va = self.angle_controller.output

        # the error vector from the robot to the target point
        error = array(self.target.coords[0]) - array(r.coords[0])
        # some crazy equation that makes the robot converge to the target point
        g = 9.80665
        mi = 0.1
        a_max = mi * g
        v_max = r.max_speed
        cte = (4 * a_max / (v_max * v_max))
        out = v_max * (1 - exp(-cte * norm(error)))
        # v is the speed vector resulting from that equation
        v = out * error / norm(error)

        # at last set the action accordingly
        r.action.absolute_speeds = v[0], v[1], va

    @property
    def point_away_from_defense_area(self):
        # FIXME: Only works if robot is inside defense area (which, honestly, is the only place you should ever be using this).
        r = self.robot

        target = Point(self.x, self.y)

        defense_area = r.world.defense_area(r.color).buffer(r.radius + 0.1).boundary
        distance = target.distance(defense_area)
        buffered_circumference = target.buffer(distance)
        intersection = buffered_circumference.intersection(defense_area).centroid
        if not intersection.is_empty:
            desired_distance = distance
            modulus = sqrt((intersection.x - self.x) * (intersection.x - self.x) + (intersection.y - self.y) * (intersection.y - self.y))
            dx = desired_distance * (intersection.x - self.x) / modulus
            dy = desired_distance * (intersection.y - self.y) / modulus
            return Point(self.x + dx, self.y + dy)
        else:
            return Point(self.x, self.y)
