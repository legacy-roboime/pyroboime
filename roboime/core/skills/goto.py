from numpy import array
from numpy.linalg import norm

from .. import Skill
from ...utils.mathutils import exp
from ...utils.geom import Point
from ...utils.pidcontroller import PidController
#import sys


class Goto(Skill):
    """
    Sends the robot to a specified point with a specified orientation with no
    regard to the position of any other objects on the field.
    """
    def __init__(self, robot, target=None, angle=None, final_target=None, is_goalkeeper=False, referential=None, deterministic=True, **kwargs):
        """
        final_target: the ultimate position the robot should attain
        target: the intermediate position you're ACTUALLY sending the robot to
        angle: the orientation the robot should have at target

        final_target is there so that, on a tactic, you can make the robot follow a curve to final_target
        while not stopping near each target due to its extreme proximity to it by continuously adjusting
        target to be ever closer to final_target. These intermediate steps are not handled by this class,
        and the exact curve you want the robot to follow (and hence all the intermediate targets that you'll
        be switching in) should be specified in your own class.
        """
        super(Goto, self).__init__(robot, deterministic=deterministic, **kwargs)
        self.is_goalkeeper = is_goalkeeper
        #TODO: find the right parameters
        self.angle_controller = PidController(kp=1.8, ki=0, kd=0, integ_max=687.55, output_max=360)
        #self.angle_controller = PidController(kp=1.324, ki=0, kd=0, integ_max=6.55, output_max=1000)
        self.angle = angle
        self.target = target
        # self.final_target = final_target if final_target is not None else self.target
        self.final_target = final_target
        self.referential = referential

    def step(self):
        r = self.robot
        t = self.target if self.target is not None else r
        f_t = self.final_target if self.final_target is not None else self.target
        #ref = self.referential if self.referential is not None else f_t
        # TODO: Check if target is within the boundaries of the field (augmented of the robot's radius).

        # check wether the point we want to go to will make the robot be in the defense area
        # if so then we'll go to the nearest point that meets that constraint
        if not self.is_goalkeeper and r.world.is_in_defense_area(body=t.buffer(r.radius), color=r.color):
            t = self.point_away_from_defense_area

        # angle control using PID controller
        if self.angle is not None:
            self.angle_controller.input = (180 + self.angle - self.robot.angle) % 360 - 180
            self.angle_controller.feedback = 0.0
            self.angle_controller.step()
            va = self.angle_controller.output
        else:
            va = 0

        # the error vector from the robot to the target point
        error = array(t.coords[0]) - array(r.coords[0])

        # some crazy equation that makes the robot converge to the target point
        g = 9.80665
        mi = 0.1
        a_max = mi * g
        v_max = r.max_speed
        cte = (4 * a_max / (v_max * v_max))
        out = v_max * (1 - exp(-cte * r.distance(f_t)))
        # v is the speed vector resulting from that equation
        v = out * error / norm(error)

        # increase by referential speed
        # not working, must think about it
        #if ref is not None:
        #    v += ref.speed

        # at last set the action accordingly
        r.action.absolute_speeds = v[0], v[1], va

    @property
    def point_away_from_defense_area(self):
        # FIXME: Only works if robot is inside defense area (which, honestly, is the only place you should ever be using this).
        # FIXME: I think I broke it, needs fixing, reviewing and commenting
        defense_area = self.world.defense_area(self.robot.color).buffer(self.robot.radius + 0.1).boundary
        distance = self.target.distance(defense_area)
        buffered_circumference = self.target.buffer(distance)
        intersection = buffered_circumference.intersection(defense_area).centroid
        if not intersection.is_empty:
            error = array(intersection) - array(self.target)
            diff = distance * error / norm(error)
            return Point(array(self.target) + diff)
        else:
            return self.target
