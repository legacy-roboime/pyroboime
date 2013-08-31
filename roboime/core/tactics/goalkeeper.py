from numpy import array
#from numpy import cross
#from numpy import dot
from numpy import sign
from numpy import linspace
from itertools import groupby

from ...utils.mathutils import sin, cos
from ...utils.geom import Line, Point
from .. import Tactic
from ..skills.gotolooking import GotoLooking
from ..skills.kickto import KickTo
from ..skills.sampledchipkick import SampledChipKick


class Goalkeeper(Tactic):
    """
    This is the goalie. Make it smart.

    If you set the aggressive mode on, guess what, it'll get angry
    when the ball is close, and kick it, kick it as far as possible
    whenever possible. Sometimes you may not want that, choose wisely.
    """
    def __init__(self, robot, aggressive=False, angle=0):
        """
        angle: this angle is how much inside the goal the goalkeeper must be
          when 0 it's completely outside, when 90, it's half inside, when 180
          it's completely inside, naturally values greater than 90 don't make much sense
        aggressive: this sets the aggressive mode, which means that the goalkeeper
          will also act as an attacker when it is the closer robot to the ball
        """

        super(Goalkeeper, self).__init__(robot, deterministic=True)
        self.aggressive = aggressive
        self.goto = GotoLooking(robot, lookpoint=robot.world.ball, target=lambda: robot.goal)
        self.kick = KickTo(robot, lookpoint=lambda: robot.enemy_goal)
        self.chip = SampledChipKick(robot, lookpoint=lambda: robot.enemy_goal)
        self.angle = angle
        # should parametrize these
        # time in seconds to predict future ball position
        self.look_ahead_time = 2.0
        self.domination_radius = 0.135
        #self.safety_ratio = 0.9
        self.safety_ratio = 2.0

    def _step(self):
        #TODO: if ball is inside area and is slow, kick/pass it far far away

        # Build the home line
        #
        #   ,-> goal
        # +-o
        # |   | <- home_line
        # |   |
        # |   |
        # +-o/_ <- angle
        #

        # Sets the ratio between the perpendicular distance of the homeline to the goal and the GK's radius
        radius = (self.robot.radius + 2 * self.ball.radius) * self.safety_ratio

        # Compute home line ends
        p1 = Point(array(self.goal.p1) + radius * array((cos(self.angle) * -sign(self.goal.x), -sin(self.angle))))
        p2 = Point(array(self.goal.p2) + radius * array((cos(self.angle) * -sign(self.goal.x), sin(self.angle))))

        # Aaaand the home line
        home_line = Line(p1, p2)

        ### Find out where in the homeline should we stay ###

        if self.aggressive:
            if self.robot is self.world.closest_robot_to_ball():
                return self.chip.step()

        # if the ball is moving fast* torwards the goal, defend it: THE CATCH
        #*: define fast

        future_ball = array(self.ball) + self.ball.speed * self.look_ahead_time
        ball_line = Line(Point(self.ball), Point(future_ball))

        if ball_line.crosses(self.goal.line):
            point_on_home = ball_line.intersection(home_line)
            if point_on_home.geom_type == 'Point':
                self.goto.target = point_on_home
            else:
                self.goto.target = p1 if p1.distance_to_line(ball_line) < p2.distance_to_line(ball_line) else p2
            return self.goto.step()

        # watch the enemy
        # TODO: get the chain of badguys, (badguy and who can it pass to)

        # if the badguy has closest reach to the ball then watch it's orientation
        danger_bot = self.world.closest_robot_to_ball()

        # If dangerBot is an enemy, we shall watch his orientation. If he's a friend, we move on to a more
        # appropriate strategy
        if danger_bot is not None and danger_bot.is_enemy(self.robot) and danger_bot.distance(self.ball) < self.domination_radius:
            # Line starting from the dangerBot spanning twice the width of the field (just to be sure)
            # to the goal with the desired orientation.
            future_point = Point(array(danger_bot) + array((cos(danger_bot.angle), sin(danger_bot.angle))) * 2 * self.world.width)
            danger_line = Line(danger_bot, future_point)

            if danger_line.crosses(self.goal.line):
                point_on_home = danger_line.intersection(home_line)
                if point_on_home.geom_type == 'Point':
                    self.goto.target = point_on_home
                else:
                    self.goto.target = p1 if p1.distance_to_line(danger_line) < p2.distance_to_line(danger_line) else p2
                return self.goto.step()
            else:
                self.goto.target = p1 if future_point.y > 0 else p2
        # else:
        # Otherwise, try to close the largest gap
        #Point blBestPoint = pointToKeep(), hlBestPoint;
        #Line ballToBlBestPoint(ball, blBestPoint);
        #if(homeline.intersect(ballToBlBestPoint, &hlBestPoint) == Line::BoundedIntersection)
        #{
        #  goto_->setPoint(hlBestPoint);
        #}
        #else
        #{
        #  if(Line(homeline.p1(), hlBestPoint).length()< Line(homeline.p2(), hlBestPoint).length())
        #  {
        #    goto_->setPoint(homeline.p1());
        #  }
        #  else
        #  {
        #    goto_->setPoint(homeline.p2());
        #  }
        #}

        # middle of the largest gap:
        p = self.point_to_defend()
        if p is not None:
            self.goto.target = self.point_to_defend()

        # continue stepping the last strategy
        self.goto.step()

    def point_to_defend(self):
        #radius = (self.robot.radius + 2 * self.ball.radius) * self.safety_ratio
        """
        This method comes from Zickler.

        The main difference is that it transfers the point to defend from the goal line to the base line.
        """
        our_goal = self.team.goal
        max_hole = []

        possible_points = [(y, self.world.has_clear_shot(Point(our_goal.x, y))) for y in linspace(our_goal.p2.y, our_goal.p1.y, 5)]

        for has_clear_shot, group in groupby(possible_points, lambda (point, has): has):
            if has_clear_shot:
                hole = list(group)
                if len(hole) >  len(max_hole):
                    max_hole = hole

        if len(max_hole) != 0:
            y = (max_hole[0][0] + max_hole[-1][0]) / 2
            #return Point(our_goal.x, y)
            # The following calculation transports the point from the goal line to the base line
            return Point(our_goal.x - sign(our_goal.x) * self.robot.radius, (our_goal.x - sign(our_goal.x) * self.robot.radius) * y / our_goal.x)
            #return Point(our_goal.x - sign(our_goal.x) * radius, (our_goal.x - sign(our_goal.x) * radius) * y / our_goal.x)
