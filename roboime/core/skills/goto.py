from numpy import array, linspace
from numpy.linalg import norm

from .. import Skill
from ...utils.geom import Point
from ...utils.pidcontroller import PidController


class Goto(Skill):
    """
    New goto using Stox's path planning
    """
    # path planning
    max_recursive = 3
    divisions = 10

    # distance to consider target arrival
    arrive_distance = 1e-3
    max_angle_error = 1.0

    def __init__(self, robot, target=None, angle=None, avoid_collisions=True,
                 **kwargs):
        super(Goto, self).__init__(robot, deterministic=True, **kwargs)
        self.angle_controller = PidController(
            kp=1., ki=.0, kd=.0, integ_max=.5, output_max=360)
        self.norm_controller = PidController(
            kp=.1, ki=0.01, kd=.5, integ_max=50., output_max=1.2)
        self.x_controller = PidController(
            kp=.3, ki=0.01, kd=.05, integ_max=5., output_max=.8)
        self.y_controller = PidController(
            kp=.3, ki=0.01, kd=.05, integ_max=5., output_max=.8)

        self.angle = angle
        self.final_target = target
        self.target = self.final_target
        self.avoid_collisions = avoid_collisions

        self.collision_distance = self.robot.radius * 1.5

    def arrived(self):
        dist = array(self.robot) - array(self.target)
        return norm(dist) <= self.arrive_distance

    def oriented(self):
        angle = (180 + self.angle - self.robot.angle) % 360 - 180
        return abs(angle) <= self.max_angle_error

    def _step(self):
        self.target = self.path_planner(self.final_target)

        # angle control using PID controller
        if self.angle is not None and self.robot.angle is not None:
            angle = (180 + self.angle - self.robot.angle) % 360 - 180
            self.angle_controller.input = angle
            self.angle_controller.feedback = 0.0
            self.angle_controller.step()
            va = self.angle_controller.output
        else:
            va = 0.0

        diff_to_final = array(self.final_target) - array(self.robot)
        diff = array(self.target) - array(self.robot)
        vel = self.robot.max_speed if norm(diff_to_final) > 0.5 else self.robot.max_speed * norm(diff)
        v = vel * diff / norm(diff)
        self.robot.action.absolute_speeds = v[0], v[1], va

    def path_planner(self, target, depth=0):
        if depth < self.max_recursive:
            diff = array(target) - array(self.robot)

            # TODO: Rewrite the python's way
            points = []
            x = linspace(target.x, self.robot.x, self.divisions)
            y = linspace(target.y, self.robot.y, self.divisions)
            for i in xrange(self.divisions):
                points.append(Point(x[i], y[i]))
            points.pop(0)

            robots = self.get_robots()
            for point in points:
                if self.point_inside_robot(point, robots):
                    # TODO: Rewrite the python's way
                    n = diff * self.collision_distance / norm(diff)
                    temp = Point(-n[1] + point.x, n[0] + point.y)
                    return self.path_planner(temp, depth + 1)
        return target

    def get_robots(self):
        return [r for r in self.world.robots if r.uid != self.robot.uid]

    def point_inside_robot(self, point, robots):
        for r in robots:
            diff = norm(array(point) - array(r))
            if diff <= 2 * self.robot.radius:
                return True
        return False
