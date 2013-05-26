from numpy import array

from .. import Tactic
from ...utils.geom import Point
from ..skills.gotolooking import GotoLooking

from ...utils.mathutils import sin
from ...utils.mathutils import cos

class Blocker(Tactic):
    """
    Follow a point, maintaining a fixed distance from it while
    covering another point. Pretty much like a follow and cover.
    """
    # TODO
    def __init__(self, robot, arc, distance=0.5, blockpoint=None):
        """
        arc: angle deviation in relation to line from robot to goal
        distance: constant distance to keep from blockpoint
        blockpoint: point to block, if none falls back to ball
        """
        super(Blocker, self).__init__([robot], deterministic=True)
        # TODO: implement with follow and cover somehow, needs angle deviantion
        self.blockpoint = self.ball if blockpoint is None else blockpoint
        self.goto = GotoLooking(self.robot, lookpoint=self.blockpoint)
        self.arc = arc
        self.dist = distance

    def step(self):
        base_angle = self.ball.angle_to_point(self.goal)
        self.goto.target = Point(array((self.dist * cos(base_angle + self.arc), self.dist * sin(base_angle + self.arc))) + array(self.blockpoint))
        self.goto.step()
