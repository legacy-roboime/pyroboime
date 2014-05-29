#
# Copyright (C) 2013 RoboIME
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
from numpy import array, sign
from numpy.linalg import norm

from .. import Skill
from ...utils.mathutils import exp
from ...utils.geom import Point
from ...utils.pidcontroller import PidController


def force_equation(direction, distance, floor, factor, power):
    return direction * (floor + factor / distance) ** power


class Goto(Skill):
    """
    Sends the robot to a specified point with a specified orientation with no
    regard to the position of any other objects on the field.
    """

    # attraction coefificients
    attraction_factor = 6.0
    attraction_power = 2.3
    attraction_floor = 80.0

    # repulsion coefificients
    repulsion_factor = 8.0
    repulsion_power = 3.3
    repulsion_floor = 0.0

    # magnetic coefificients
    magnetic_factor = 9.0
    magnetic_power = 3.1
    magnetic_floor = 0.0

    # delta_speed coefificients
    delta_speed_factor = 2.0
    delta_speed_power = 1.4
    delta_speed_floor = 0.0

    # minimum distance to use on the equation
    # anything smaller is capped to this
    min_distance = 1e-5

    # distance to consider target arrival
    arrive_distance = 1e-3
    max_angle_error = 1.0

    # ignore other forces if attraction
    # force is as least this high:
    min_force_to_ignore_others = 100000

    # control params
    g = 9.80665
    mi = 0.1
    exp_k = 6

    #def __init__(self, robot, target=None, angle=None, final_target=None, referential=None, deterministic=True, avoid_collisions=True, **kwargs):
    def __init__(self, robot, target=None, angle=None, final_target=None, referential=None, deterministic=True, avoid_collisions=False, use_norm_pid=False, separate_axis_control=False, **kwargs):
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
        self.angle_controller = PidController(kp=1., ki=.0, kd=.0, integ_max=.5, output_max=360)
        self.norm_controller = PidController(kp=.1, ki=0.01, kd=.5, integ_max=50., output_max=1.2)
        self.x_controller = PidController(kp=.3, ki=0.01, kd=.05, integ_max=5., output_max=.8)
        self.y_controller = PidController(kp=.3, ki=0.01, kd=.05, integ_max=5., output_max=.8)
        self.use_norm_pid = use_norm_pid
        self.separate_axis_control = separate_axis_control
        #self.angle_controller = PidController(kp=1.324, ki=0, kd=0, integ_max=6.55, output_max=1000)
        self._angle = angle
        self._target = target
        self.target = target
        # self.final_target = final_target if final_target is not None else self.target
        self.final_target = final_target
        self.referential = referential
        self.avoid_collisions = avoid_collisions

    def arrived(self):
        return norm(array(self.robot) - array(self.target)) <= self.arrive_distance

    def oriented(self):
        return (180 + self.angle - self.robot.angle) % 360 - 180 <= self.max_angle_error

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
        delta = array(self.target) - array(self.robot)

        # attractive force
        dist = max(self.robot.distance(self.final_target), self.min_distance)

        # normalize delta
        delta /= dist

        #attraction_force = delta * (1 + 1 / (dist / self.attraction_factor) ** self.attraction_power)
        #attraction_force = delta * (self.attraction_floor + (self.attraction_factor / dist) ** self.attraction_power)
        attraction_force = force_equation(delta, dist, self.attraction_floor, self.attraction_factor, self.attraction_power)

        return attraction_force

    def other_forces(self):
        robot = self.robot
        for other in filter(lambda other: other is not robot, self.world.iterrobots()):
            # difference of position
            delta = array(robot) - array(other)

            # considered distance
            dist = norm(delta) + robot.radius + other.radius

            # cap the distance to a minimum of 1mm
            dist = max(dist, self.min_distance)

            # normalize the delta
            delta /= norm(delta)

            # perpendicular delta
            pdelta = array((delta[1], -delta[0]))

            # normalized difference of speeds of the robots
            sdelta = other.speed - robot.speed
            sdelta /= max(norm(sdelta), self.min_distance)

            # calculating each force
            #repulsion_force = delta * (self.repulsion_factor / dist) ** self.repulsion_power
            repulsion_force = force_equation(delta, dist, 0, self.repulsion_factor, self.repulsion_power)
            #magnetic_force = pdelta * (self.magnetic_factor / dist) ** self.magnetic_power
            magnetic_force = force_equation(pdelta, dist, 0, self.magnetic_factor, self.magnetic_power)
            #delta_speed_force = sdelta * (self.delta_speed_factor / dist) ** self.delta_speed_power
            delta_speed_force = force_equation(sdelta, dist, 0, self.delta_speed_factor, self.delta_speed_power)
            yield (repulsion_force, magnetic_force, delta_speed_force)

    def _step(self):
        r = self.robot
        t = self.target
        f_t = self.final_target
        #ref = self.referential if self.referential is not None else f_t
        # TODO: Check if target is within the boundaries of the field (augmented of the robot's radius).

        # check whether the point we want to go to will make the robot be in the defense area
        # if so then we'll go to the nearest point that meets that constraint
        #print "ball is in area?", r.world.is_in_defense_area(body=self.world.ball.buffer(r.radius), color=r.color)
        if not self.robot.is_goalie and r.world.is_in_defense_area(body=t.buffer(r.radius), color=r.color):
            self.target = self.point_away_from_defense_area
            t = self.target

        # angle control using PID controller
        if self.angle is not None and self.robot.angle is not None:
            self.angle_controller.input = (180 + self.angle - self.robot.angle) % 360 - 180
            #self.angle_controller.input = (180 + 0 - self.robot.angle) % 360 - 180
            self.angle_controller.feedback = 0.0
            self.angle_controller.step()
            va = self.angle_controller.output
        else:
            va = 0.0

        # the error vector from the robot to the target point
        error = array(t) - array(r)

        # the gradient of the field
        gradient = self.attraction_force()
        if norm(gradient) < self.min_force_to_ignore_others:
            gradient += sum(map(sum, self.other_forces()))
        # WTF
        if self.separate_axis_control:
            delta = array(f_t) - array(r)
            ghost_point = norm(delta) * gradient / norm(gradient)
            print gradient
            print ghost_point
            self.x_controller.input = ghost_point[0]
            self.y_controller.input = ghost_point[1]
            self.x_controller.feedback = 0.
            self.y_controller.feedback = 0.
            self.x_controller.step()
            self.y_controller.step()
            r.action.absolute_speeds = self.x_controller.output, self.y_controller.output, va
            print r.action.absolute_speeds

        else:
            if self.use_norm_pid:
                distance = norm(array(f_t) - array(r))
                self.norm_controller.input = distance
                self.norm_controller.feedback = 0.
                self.norm_controller.step()
                out = self.norm_controller.output
            else:
                # some crazy equation that makes the robot converge to the target point
                a_max = self.mi * self.g
                v_max = r.max_speed
                cte = (self.exp_k * a_max / (v_max * v_max))
                out = v_max * (1 - exp(-cte * r.distance(f_t)))
            # v is the speed vector resulting from that equation
            #print out
            if self.avoid_collisions:
                v = out * gradient / norm(gradient)
            else:
                # v = out * normalized error
                # must check if error is zero lengthed
                v = error
                ne = norm(error)
                if ne != 0:
                    v *= out / ne

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
        defense_area = self.world.augmented_defense_area(self.robot, self.robot.color).boundary
        distance = self.target.distance(defense_area)
        buffered_circumference = self.target.buffer(distance)
        intersection = buffered_circumference.intersection(defense_area).centroid
        if not intersection.is_empty:
        #    if abs(self.target.x) < abs(self.world.goal(self.robot.color).x):
            #print 'case 1'
            error = array(intersection) - array(self.target)
            diff = distance * error / norm(error)
            #print "returning point from defense area"
            return Point(array(self.target) + diff)
        #    else:
        #        print 'case 2'
        #        return Point(self.target.x - 2 * sign(self.goal.x) * self.world.defense_radius, self.robot.y)
        #        #diff = -1 * distance * error / norm(error)
        #        #print "returning point from defense area"
        #        #return Point(array(self.target) + 2 * diff)
        else:
            return self.target
