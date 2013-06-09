"""
This module holds the base classes.

Things worth knowing:

uid in this context means unique id, it is unique within a team only
uuid in this context is universal unique id, it is unique whithin a world
"""
from itertools import imap
from collections import defaultdict
from functools import partial
from numpy import array
from numpy import sign
from shapely import geometry

from .utils import geom
from .utils.mathutils import cos, sin


# this codes are used to compute the uid
# of a robot to make it unique even comparing
# robots of different teams
Yellow = 0x1e11000
Blue = 0xb100e00


class Component(object):
    """Use this class to build components such as kicker or dribbler"""

    def __init__(self):
        self.working = None
        self.active = None

    @property
    def broken(self):
        return not self.working if self.working is not None else None


class Action(object):
    """An instance of this class determines what will a robot do."""

    def __init__(self, robot, target=None, speeds=None):
        """
        The action can do a veeery rudimentary control, for that one has to set
        a target instead of the speeds.

        For going to the point x=3, y=5 with and angle=30:
        >>> a = Action(target=(3.0, 5.0, 30.0))

        This will also work:
        >>> a.target = (3.0, 5.0, 30.0)

        It is more appropriate to do a real control apart and have it set the speeds,
        the speeds are in the robot's referential paralel, normal and angular
        respectively. To have it go straight with speed 1.0:
        >>> a = Action(speeds=(1.0, 0.0, 0.0))

        One can also use the speeds property, to have it spin still for instance:
        >>> a.speeds = (0.0, 0.0, 2.0)
        """
        self.robot = robot
        self.x, self.y, self.angle = target if target is not None else (None, None, None)
        self.kick = None
        self.chipkick = None
        self.dribble = None
        self._speeds = speeds

    def reset(self):
        self._speeds = None
        self.kick = None
        self.chipkick = None
        self.dribble = None
        self._speeds = None

    @property
    def target(self):
        return self.x, self.y, self.angle

    def __nonzero__(self):
        """This is used for implicit bool conversion, which answers if the action does something."""
        return not (self.x is None or self.y is None or self.angle is None) or self._speeds is not None

    @target.setter
    def target(self, t):
        self._speeds = None
        self.x, self.y, self.angle = t if t is not None else (None, None, None)

    @property
    def uid(self):
        return self.robot.uid

    @property
    def color(self):
        return self.robot.color

    @property
    def speeds(self):
        if self._speeds is not None:
            return tuple(self._speeds)
        else:
            # This is deprecated and can be removed at any time. Use goto instead.
            s = self.robot.max_speed
            #TODO: implement some PID, should this be really here?
            if not self:
                return (0.0, 0.0, 0.0)
            x, y, a = self.target
            r = self.robot
            #import pudb; pudb.set_trace()
            ra = r.angle
            va = 0.2 * (a - ra)
            vx, vy = x - r.x, y - r.y
            vx, vy = vx * cos(ra) + vy * sin(ra), vy * cos(ra) - vx * sin(ra)
            return tuple(map(lambda t: s * t, (vx, vy, va)))

    @speeds.setter
    def speeds(self, speeds):
        self._speeds = speeds

    @property
    def absolute_speeds(self):
        vx, vy, va = self._speeds
        ra = self.robot.angle
        return (vx * cos(ra) - vy * sin(ra), vy * cos(ra) + vx * sin(ra), va)

    @absolute_speeds.setter
    def absolute_speeds(self, speeds):
        vx, vy, va = speeds
        ra = self.robot.angle
        self._speeds = (vx * cos(ra) + vy * sin(ra), vy * cos(ra) - vx * sin(ra), va)


class Robot(geom.Point):

    def __init__(self, uid, body=None, dribbler=None, kicker=None, wheels=[], battery=None, team=None, max_speed=5.0, max_ang_speed=10.0):
        """This class represents a robot, regardless of the team.

        Remember to set max_speed and max_ang_speed to reasonable limits.
        """
        super(Robot, self).__init__(0.0, 0.0)
        # TODO make a robot builder/factory to abstract these sizes
        self._radius = 180e-3 / 2
        self.front_cut = self._radius * 0.7
        self.max_speed = max_speed
        self.max_ang_speed = max_ang_speed

        # ideally robot should inherit from a class that has an angle
        # and some geometry framework can use that angle
        self.angle = None
        self.speed = None
        self.active = False

        # basic
        self.uid = uid
        self.pattern = None
        self.team = team

        # components
        self.dribbler = dribbler
        self.kicker = kicker
        self.wheels = wheels
        self.battery = battery

        # initial body
        self._body = geom.Circle(self, self._radius)

        # action to be dispatched by a commander
        self._action = Action(self)

        # last skill that was executed
        self.skill = None

        # some properties
        self.can_kick = True

    def update(self, *args, **kwargs):
        """This is just a hook over the original function to cache some data."""
        super(Robot, self).update(*args, **kwargs)
        # TODO generate the actual body shape instead of a circle
        self._body = geom.Circle(self, self._radius)

    @property
    def enemy_team(self):
        return self.team.enemy_team if self.team is not None else None

    @property
    def enemy_goal(self):
        return self.team.enemy_goal if self.team is not None else None

    @property
    def is_blue(self):
        return self.color == Blue

    @property
    def is_yellow(self):
        return self.color == Yellow

    @property
    def body(self):
        return self._body

    @property
    def action(self):
        return self._action

    @property
    def height(self):
        return self.body.height if self.body else None

    @property
    def radius(self):
        return self._radius

    @property
    def color(self):
        if self.team is not None:
            return self.team.color
        else:
            # this means that this robot
            # is not within a team, but it's
            # color can be used to operate
            return 0

    @property
    def uuid(self):
        return self.uid + self.color

    @property
    def goal(self):
        if self.team is not None:
            return self.team.goal
        else:
            return None

    @property
    def world(self):
        if self.team is not None:
            return self.team.world
        else:
            return None

    def is_enemy(self, robot):
        """Name says it all."""
        return self.team.color != robot.team.color

    def step(self):
        if self._skill is not None:
            self._skill.step()


class Team(defaultdict):
    """This is basically a list of robots."""

    def __init__(self, color, robots=[], world=None):
        super(Team, self).__init__(partial(Robot, team=self), imap(lambda r: (r.pattern, r), robots))

        self.color = color
        self.world = world

        # update robots' team
        for r in self.itervalues():
            r.team = self

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        else:
            val = self[key] = self.default_factory(key)
            return val

    @classmethod
    def blue(cls, *args, **kwargs):
        return cls(Blue, *args, **kwargs)

    @classmethod
    def yellow(cls, *args, **kwargs):
        return cls(Yellow, *args, **kwargs)

    @property
    def goal(self):
        return self.world.goal(self.color)

    @property
    def enemy_goal(self):
        return self.world.enemy_goal(self.color)

    @property
    def enemy_team(self):
        return self.world.enemy_team(self.color)

    @property
    def is_blue(self):
        return self.color == Blue

    @property
    def is_yellow(self):
        return self.color == Yellow

    def iterrobots(self, active=True):
        for r in self.itervalues():
            if active is not None:
                if r.active == active:
                    yield r
            else:
                yield r

    def closest_robots_to_ball(self, **kwargs):
        return self.world.closest_robots_to_ball(color=self.color, **kwargs)

    def closest_robots_to_point(self, point, **kwargs):
        return self.world.closest_robots_to_point(point, color=self.color, **kwargs)

    def __iter__(self):
        return self.iterrobots(active=True)


class Ball(geom.Point):
    """Well, a ball."""

    def __init__(self, world):
        super(Ball, self).__init__(0.0, 0.0)
        self._radius = 43e-3 / 2
        self.world = world
        self.speed = array((0.0, 0.0))

        # initial body
        self._body = geom.Circle(self, self._radius)

    def update(self, *args, **kwargs):
        """This is just a hook over the original function to cache some data."""
        super(Ball, self).update(*args, **kwargs)
        self._body = geom.Circle(self, self._radius)

    @property
    def body(self):
        return self._body

    @property
    def radius(self):
        return self._radius


class Goal(geom.Point):
    """
    The goal is a point, hurray!
    But it also got two posts, and a body. Like this:

             +-o <-- p1
             |
    body --> | x <-- self (as a point)
             |
             +-o <-- p2

    The body is a shapely.geometry.LineString that begins
    on p1 ending on p2, it forms a squared C shape.

    As a LineString it contains only points over its line,
    but if one wants to check if an object is inside the goal
    its convex hull should be used.

    Example usage:

    >>> w = World()
    >>> w.goal_depth = 1.0
    >>> w.goal_width = 3.0
    >>> g = Goal(w, 0.0, 0.0)
    >>> array(g)
    array([ 0.,  0.])
    >>> array(g.p1)
    array([ 0.,  1.5])
    >>> array(g.body)
    array([[ 0. ,  1.5],
           [ 1. ,  1.5],
           [ 1. , -1.5],
           [ 0. , -1.5]])
    >>> p = geom.Point(0.5, 0.0)
    >>> g.body.convex_hull.contains(p)
    True
    >>> p = geom.Point(-0.5, 0.0)
    >>> g.body.convex_hull.contains(p)
    False
    """
    def __init__(self, world, *args):
        super(Goal, self).__init__(0.0, 0.0)
        self.world = world
        self.update(0.0, 0.0)
        #self._p1 = geom.Point(0, 0)
        #self._p2 = geom.Point(0, 0)
        #self._line = geom.Line(self._p1, self._p2)
        #self._body = geometry.LineString
        if len(args) > 0:
            self.update(*args)

    def update(self, *args, **kwargs):
        """This is just a hook over the original function to cache some data."""
        super(Goal, self).update(*args, **kwargs)
        self._p1 = geom.Point(array(self) + array((0.0, self.width / 2)))
        self._p2 = geom.Point(array(self) - array((0.0, self.width / 2)))
        self._line = geom.Line(self._p1, self._p2)
        self._body = geometry.LineString([
            array(self) + array((0.0, self.width / 2)),
            array(self) + array((self.depth * (sign(self.x) or 1), self.width / 2)),
            array(self) + array((self.depth * (sign(self.x) or 1), -self.width / 2)),
            array(self) + array((0.0, -self.width / 2)),
        ])

    @property
    def line(self):
        return self._line

    @property
    def body(self):
        return self._body

    @property
    def p1(self):
        return self._p1

    @property
    def p2(self):
        return self._p2

    @property
    def width(self):
        return self.world.goal_width

    @property
    def depth(self):
        return self.world.goal_depth

    @property
    def wall_width(self):
        return self.world.goal_wall_width


class Referee(object):
    class Stage:
        FirstHalf = 'FirstHalf'
        HalfTime = 'HalfTime'
        SecondHalf = 'SecondHalf'
        OvertimeFirstHalf = 'OvertimeFirstHalf'
        OvertimeSecondHalf = 'OvertimeSecondHalf'
        Penalty = 'Penalty'

    class Mode:
        Halt = 'Halt'
        Stop = 'Stop'
        Start = 'Start'

    def __init__(self, world):
        self.world = world
        self.stage = None
        self.control = None


class World(object):

    def __init__(self, right_team=None, left_team=None):
        # metric constants
        self.width = 0.0
        self.length = 0.0
        self.line_width = 0.0
        self.boundary_width = 0.0
        self.referee_width = 0.0
        self.center_radius = 0.0
        self.defense_radius = 0.0
        self.defense_stretch = 0.0
        self.free_kick_distance = 0.0
        self.penalty_spot_distance = 0.0
        self.penalty_line_distance = 0.0
        self.goal_width = 0.0
        self.goal_depth = 0.0
        self.goal_wall_width = 0.0
        self.inited = False

        # objects
        if right_team is None:
            self.right_team = Team.yellow(world=self)
        else:
            right_team.world = self
            self.right_team = right_team
        if left_team is None:
            self.left_team = Team.blue(world=self)
        else:
            left_team.world = self
            self.left_team = left_team
        self.right_goal = Goal(self)
        self.left_goal = Goal(self)
        self.referee = None
        self.ball = Ball(self)

        # the referee
        self.referee = Referee(self)

    def switch_sides(self):
        self.right_team, self.left_team = self.left_team, self.right_team

    def has_clear_shot(self, point_to_kick):
        shot_line = geom.Line(self.ball, point_to_kick)
        for robot in self.iterrobots():
            if shot_line.crosses(robot.body):
                return False
        return True

    @property
    def yellow_team(self):
        return self.team(Yellow)

    @property
    def blue_team(self):
        return self.team(Blue)

    def team(self, color):
        if self.right_team.color == color:
            return self.right_team
        elif self.left_team.color == color:
            return self.left_team
        else:
            raise Exception

    def enemy_team(self, color):
        if self.right_team.color == color:
            return self.left_team
        elif self.left_team.color == color:
            return self.right_team
        else:
            raise Exception

    @property
    def yellow_goal(self):
        return self.goal(Yellow)

    @property
    def blue_goal(self):
        return self.goal(Blue)

    def goal(self, color):
        if self.right_team.color == color:
            return self.right_goal
        elif self.left_team.color == color:
            return self.left_goal
        else:
            raise Exception

    def enemy_goal(self, color):
        if self.right_team.color == color:
            return self.left_goal
        elif self.left_team.color == color:
            return self.right_goal
        else:
            raise Exception

    def is_in_defense_area(self, robot=None, body=None, color=None):
        if body and color:
            return not self.defense_area(color).intersection(body).is_empty
        elif robot:
            return self.defense_area(robot.color).contains(robot) or not self.defense_area(robot.color).intersection(robot.body).is_empty

    def defense_area(self, color):
        goal = self.goal(color)
        gx, gy = goal.x, goal.y
        #goal_width = self.goal_width
        defense_area_radius = self.defense_radius
        defense_area_stretch = self.defense_stretch
        line_to_buffer = geom.Line([(gx, gy + defense_area_stretch / 2), (gx, gy - defense_area_stretch / 2)])
        return line_to_buffer.buffer(defense_area_radius)

    def closest_robot_to_ball(self, **kwargs):
        return self.closest_robot_to_point(self.ball, **kwargs)

    def closest_robot_to_point(self, point, can_kick=True, color=None):
        """
        Name says almost it all.
        can_kick: By default only robots that can_kick are considered.
          If can_kick is set to False, only robots that cannot kick are considered.
          If you want to consider both set can_kick to None.
        color: If specified will only consider robots from matching color.
        """
        d, r = min((r.distance(point), r) for r in self.iterrobots(can_kick=can_kick, color=color))
        return r

    def closest_robots_to_ball(self, **kwargs):
        return self.closest_robots_to_point(self.ball, **kwargs)

    def closest_robots_to_point(self, point, can_kick=True, color=None):
        """
        Name says almost it all.
        By default only robots that can_kick are considered.
        If can_kick is set to False, only robots that cannot kick are considered.
        If you want to consider both set can_kick to None.
        It will return a list sorted by distance
        """
        return [r for d, r in sorted((r.distance(point), r) for r in self.iterrobots(can_kick=can_kick, color=color))]

    @property
    def robots(self):
        return list(self.iterrobots())

    def iterrobots(self, can_kick=None, active=True, color=None):
        """W.iterrobots() -> an iterator over the robots of the world W."""
        teams = (self.right_team, self.left_team) if color is None else (self.team(color),)
        for t in teams:
            for r in t.iterrobots(active=active):
                if can_kick is None:
                    yield r
                else:
                    if r.can_kick == can_kick:
                        yield r

    def iterobjects(self):
        """W.iterobjects() -> an iterator over the objects of the world W."""
        yield self.ball
        for t in (self.right_team, self.left_team):
            for r in t.iterrobots():
                yield r

    def __iter__(self):
        return self.iterobjects()
