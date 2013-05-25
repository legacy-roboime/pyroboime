from .. import Tactic
from ...utils.geom import Point
from ..skills.goto import Goto

from ...utils.mathutils import sin
from ...utils.mathutils import cos

class Blocker(Tactic):
    """
    Follow a point, maintaining a fixed distance from it while
    covering another point. Pretty much like a follow and cover.
    """
    # TODO
    def __init__(self, robots, arc, dist=0.5):
        super(Blocker, self).__init__(robots, deterministic=True)
        # self.robot = robot
        self.arc = arc
        self.dist = dist

    def step(self):
        ball = self.ball
        my_goal = self.goal
        dist = self.dist
        arc = self.arc
        base_angle = Point.angle_orientation(ball, my_goal)
        target = Point(dist * cos(base_angle + arc), dist * sin(base_angle + arc))
        # the final robot orientation:
        angle = (base_angle + 180.0) % 360.0
        goto = Goto(self.robot, target, angle)
        goto.step()