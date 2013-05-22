from numpy import array

from .goto import Goto
from ...utils.geom import Line


class GotoAvoid(Goto):
    def __init__(self, robot, target, avoid, angle=None):
        """
        target is a point to which you want to go, and avoid
        a point which, naturally, you want to avoid
        """
        super(GotoAvoid, self).__init__(robot, target, angle=angle, final_target=target)
        self.avoid = avoid

    def step(self):
        r = self.robot
        a = self.avoid
        t = self.final_target
        #print 'AVOID', array(a.coords)

        # TODO add error margin
        avoid_radius = r.radius + self.world.ball.radius + 2.

        # If the robot can go straight to the target unimpeded by avoid, do so.
        if not a.buffer(avoid_radius).crosses(Line(r, t)):
            p = t
            print 'STUPID'
        else:
            # find the tangent point to avoid's circumference
            circ_avoid = a.buffer(r.radius).boundary
            circ_robot_avoid = r.buffer(r.distance(a)).boundary
            inter = circ_avoid.intersection(circ_robot_avoid)
            if len(inter) == 2:
                p1, p2 = circ_avoid.intersection(circ_robot_avoid)
                p = p1 if p1.distance(a) < p2.distance(a) else p2
                #print "I'm outside! ", 'tangent: ', array(p), 'target:', array(t)
            else:
                # in this case the robot is inside the avoidance circle
                # we calculate the normal segment to the line from the robot
                # to the avoid point which has its ends on the bounding circle
                normal = Line(r, a).normal_vector()
                p1, p2 = array(r) + normal * avoid_radius, array(r) - normal * avoid_radius
                p = p1 if p1.distance(t) < p2.distance(t) else p2
                #print "I'm living in the edge! ", 'tangent: ', array(p), 'target:', array(t)
        self.target = p
        super(GotoAvoid, self).step()
