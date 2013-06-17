from numpy import array

from .goto import Goto
from ...utils.mathutils import cos, sin
from ...utils.geom import Point


class FishingRod(Goto):
    def __init__(self, robot, b_angle, t_angle=None, threshold=5):
        """
        threshold: fixed distance
        b_angle: base angle, driving orientation
        b_point: base point, the robot itself
        t_angle: target angle, robot facing angle
        target: target point
        """

        super(FishingRod, self).__init__(robot, angle=t_angle)

        self.b_angle = b_angle
        self.threshold = threshold
        self.t_angle = t_angle
        # ignoreBrake = False...
        # deterministic=True ...boolean that indicates that we're dealing whit a deterministic skill...

    def _step(self):
        # Goes indefinitely on a determined angle:
        r = self.robot
        b_a = self.b_angle
        t = self.threshold

        self.angle = self.t_angle if self.t_angle is not None else b_a

        unreachable = array([r.x + t * cos(b_a), r.y + t * sin(b_a)])
        self.target = Point(unreachable)

        super(FishingRod, self)._step()
