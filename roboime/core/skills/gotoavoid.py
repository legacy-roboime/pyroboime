from numpy import array

from .goto import Goto
from ...utils.geom import Line
from ...utils.geom import Point


class GotoAvoid(Goto):
    def __init__(self, robot, target=None, avoid=None, angle=None, **kwargs):
        """
        target is a point to which you want to go, and avoid
        a point which, naturally, you want to avoid.

        If you want to temporarily set a point to not be avoided: for example,
        if you want to approach the ball, but only from behind it, when you get
        behind the ball, you can set should_avoid to False.
        """
        super(GotoAvoid, self).__init__(robot, target, angle=angle, **kwargs)
        self.avoid = avoid
        self.should_avoid = True
    
    @property
    def avoid_radius(self):
        return self.robot.radius + self.world.ball.radius + .02

    def _step(self):
        r = self.robot
        a = self.avoid
        t = self.final_target

        # TODO add error margin
        if self.avoid is not None and self.should_avoid:
            avoid_radius = self.avoid_radius
            # If the robot can go straight to the target unimpeded by avoid, do so.
            if not a.buffer(avoid_radius).crosses(Line(r, t)):
                p = t
            else:
                # find the tangent point to avoid's circumference
                circ_avoid = a.buffer(avoid_radius + .05).boundary
                circ_robot_avoid = r.buffer(r.distance(a)).boundary
                inter = circ_avoid.intersection(circ_robot_avoid)
                if len(inter) == 2:
                    p1, p2 = circ_avoid.intersection(circ_robot_avoid)
                    p = p1 if p1.distance(t) < p2.distance(t) else p2
                    p = p1
                else:
                    # in this case the robot is inside the avoidance circle
                    # we calculate the normal segment to the line from the robot
                    # to the avoid point which has its ends on the bounding circle
                    normal = Line(r, a).normal_vector()
                    p1, p2 = Point(array(r) + normal * avoid_radius), Point(array(r) - normal * avoid_radius)
                    p = p1 if p1.distance(t) < p2.distance(t) else p2
            self.target = p
        super(GotoAvoid, self)._step()
