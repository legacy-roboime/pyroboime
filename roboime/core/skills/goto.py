from numpy import array
from numpy.linalg import norm

from .. import Skill
from ...utils.mathutils import exp
from ...utils.geom import Point
from ...utils.pidcontroller import PidController


class Goto(Skill):
    """
    Sends the robot to a specified point with a specified orientation with no
    regard to the position of any other objects on the field.
    """

    attraction_factor = 12.0
    repulsion_factor = 3.0
    magnetic_factor = 3.0
    delta_speed_factor = 0.0


    def __init__(self, robot, target=None, angle=None, final_target=None, referential=None, deterministic=True, avoid_collisions=True, **kwargs):
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
        #TODO: find the right parameters
        self.angle_controller = PidController(kp=1.8, ki=0, kd=0, integ_max=687.55, output_max=360)
        #self.angle_controller = PidController(kp=1.324, ki=0, kd=0, integ_max=6.55, output_max=1000)
        self._angle = angle
        self._target = target
        self.target = target
        # self.final_target = final_target if final_target is not None else self.target
        self.final_target = final_target
        self.referential = referential
        self.avoid_collisions = avoid_collisions

    @property
    def angle(self):
        if callable(self._angle):
            return self._angle()
        else:
            return self._angle or self.robot.angle

    @angle.setter
    def angle(self, angle):
        self._angle = angle

    @property
    def target(self):
        if callable(self._target):
            return self._target()
        else:
            return self._target or self.robot

    @target.setter
    def target(self, target):
        self._target = target

    @property
    def final_target(self):
        if callable(self._final_target):
            return self._final_target()
        else:
            return self._final_target or self.target

    @final_target.setter
    def final_target(self, target):
        self._final_target = target

    def attraction_force(self):
        # the error vector from the robot to the target point
        error = array(self.target) - array(self.robot)

        # attractive force
        error_norm = max(self.robot.distance(self.final_target), 1e-3)
        attraction_force = self.attraction_factor * error * (3 + 1 / error_norm ** 2)

        return attraction_force

    def other_forces(self):
        robot = self.robot
        for other in filter(lambda other: other is not robot, self.world.iterrobots()):
            # difference of position
            delta = array(other) - array(robot)
            # considered distance
            dist = norm(delta) + robot.radius + other.radius
            # cap the distance to a minimum of 1mm
            dist = max(dist, 1e-3)
            # normalize the delta
            delta /= norm(delta)
            # perpendicular delta
            pdelta = array(delta[1], -delta[0])
            # normalized difference of speeds of the robots
            sdelta = other.speed - robot.speed
            sdelta /= max(norm(sdelta), 1e-3)

            # calculating each force
            repulsion_force = -self.repulsion_factor * delta / dist ** 2
            magnetic_force = self.magnetic_factor * pdelta / dist ** 2
            delta_speed_force = self.delta_speed_factor * sdelta / dist ** 2
            force = sum((repulsion_force, magnetic_force, delta_speed_force))
            yield force

    def _step(self):
        r = self.robot
        t = self.target
        f_t = self.final_target
        #ref = self.referential if self.referential is not None else f_t
        # TODO: Check if target is within the boundaries of the field (augmented of the robot's radius).

        # check wether the point we want to go to will make the robot be in the defense area
        # if so then we'll go to the nearest point that meets that constraint
        if not self.robot.is_goalie and r.world.is_in_defense_area(body=t.buffer(r.radius), color=r.color):
            t = self.point_away_from_defense_area

        # angle control using PID controller
        self.angle_controller.input = (180 + self.angle - self.robot.angle) % 360 - 180
        self.angle_controller.feedback = 0.0
        self.angle_controller.step()
        va = self.angle_controller.output

        # the error vector from the robot to the target point
        error = array(t) - array(r)

        # the gradient of the field
        gradient = self.attraction_force() + sum(self.other_forces())

        # some crazy equation that makes the robot converge to the target point
        g = 9.80665
        mi = 0.1
        a_max = mi * g
        v_max = r.max_speed
        cte = (4 * a_max / (v_max * v_max))
        out = v_max * (1 - exp(-cte * r.distance(f_t)))
        # v is the speed vector resulting from that equation
        if self.avoid_collisions:
            v = out * gradient / norm(gradient)
        else:
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
