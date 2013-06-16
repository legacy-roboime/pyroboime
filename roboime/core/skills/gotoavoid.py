from numpy import array

from .goto import Goto
from ...utils.geom import Line
from ...utils.geom import Point


class GotoAvoid(Goto):
    def __init__(self, robot, target=None, avoid=None, angle=None, **kwargs):
        """
        target is a point to which you want to go, and avoid
        a point which, naturally, you want to avoid
        """
        super(GotoAvoid, self).__init__(robot, target, angle=angle, final_target=target, **kwargs)
        self.avoid = avoid

    def _step(self):
        r = self.robot
        a = self.avoid
        t = self.final_target

        # TODO add error margin
        if self.avoid is not None:
            avoid_radius = r.radius + self.world.ball.radius + .02
            # If the robot can go straight to the target unimpeded by avoid, do so.
            if not a.buffer(avoid_radius).crosses(Line(r, t)):
                p = t
            else:
                # find the tangent point to avoid's circumference
                circ_avoid = a.buffer(avoid_radius+.05).boundary
                circ_robot_avoid = r.buffer(r.distance(a)).boundary
                inter = circ_avoid.intersection(circ_robot_avoid)
                if len(inter) == 2:
                    p1, p2 = circ_avoid.intersection(circ_robot_avoid)
                    p = p1 if p1.distance(a) < p2.distance(a) else p2
                else:
                    # in this case the robot is inside the avoidance circle
                    # we calculate the normal segment to the line from the robot
                    # to the avoid point which has its ends on the bounding circle
                    print 'oshit'
                    normal = Line(r, a).normal_vector()
                    p1, p2 = Point(array(r) + normal * avoid_radius), Point(array(r) - normal * avoid_radius)
                    p = p1 if p1.distance(t) < p2.distance(t) else p2
            self.target = p
        else:
            self.target = t
        super(GotoAvoid, self)._step()
