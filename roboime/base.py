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
"""
This module holds the base classes.

Things worth knowing:

uid in this context means unique id, it is unique within a team only
uuid in this context is universal unique id, it is unique whithin a world
"""
from itertools import imap
#from collections import defaultdict
from functools import partial
from numpy import array
from numpy import sign
from numpy import linspace
#from numpy import sign
from shapely import geometry

from .utils import geom
from .utils.mathutils import cos, sin, sqrt
from .utils.keydefaultdict import keydefaultdict
from .communication.protos.referee_pb2 import SSL_Referee as ref
from .config import config

MAX_ROBOT_SPEED = config['robot']['max_speed']


# this codes are used to compute the uid
# of a robot to make it unique even comparing
# robots of different teams
Yellow = 0x1e11000
Blue = 0xb100e00


class Rules(object):
    max_conduction_distance = 0.5


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

    def __init__(self, uid_robot, target=None, speeds=None):
        """
        The action can do a veeery rudimentary control, for that one has to set
        a target instead of the speeds. This feature is deprecated and may be
        removed at any time. Pass the x, y, angular speeds to the action instead
        when creating it.

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
        if isinstance(uid_robot, int):
            self._uid = uid_robot
            self.robot = None
        else:
            self._uid = None
            self.robot = uid_robot
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

    def __nonzero__(self):
        """This is used for implicit bool conversion, which answers if the action does something."""
        #return not (self.x is None or self.y is None or self.angle is None) or self._speeds is not None
        return self.has_target or self.has_speeds

    @property
    def target(self):
        if self.has_target:
            return self.x, self.y, self.angle
        else:
            return None

    @target.setter
    def target(self, t):
        self._speeds = None
        self.x, self.y, self.angle = t

    @property
    def has_target(self):
        return (self.x, self.y, self.angle) is not (None, None, None)

    @property
    def has_speeds(self):
        return self._speeds is not None

    @property
    def uid(self):
        if self.robot is None:
            return self._uid
        else:
            return self.robot.uid

    @property
    def color(self):
        return self.robot.color

    @property
    def speeds(self):
        return self._speeds or (0.0, 0.0, 0.0)

    @speeds.setter
    def speeds(self, speeds):
        self._speeds = speeds

    @property
    def absolute_speeds(self):
        vx, vy, va = self.speeds
        ra = self.robot.angle
        return (vx * cos(ra) - vy * sin(ra), vy * cos(ra) + vx * sin(ra), va)

    @absolute_speeds.setter
    def absolute_speeds(self, speeds):
        vx, vy, va = speeds
        ra = self.robot.angle or 0.0
        self._speeds = (vx * cos(ra) + vy * sin(ra), vy * cos(ra) - vx * sin(ra), va)

    def __str__(self):
        #return "Action: "+str(type(self.robot))+ str(self.speeds)#{'x': self.x, 'y': self.y, 'angle':self.angle})
        return "Action: {}{}".format(type(self.robot), str(self.speeds))


class Robot(geom.Point):

    max_speed = MAX_ROBOT_SPEED
    max_speed_dribbling = MAX_ROBOT_SPEED * 0.75
    max_ang_speed = 10.0

    def __init__(self, uid, body=None, dribbler=None, kicker=None, wheels=[], battery=None, team=None, max_speed=None, max_ang_speed=None):
        """This class represents a robot, regardless of the team.

        Remember to set max_speed and max_ang_speed to reasonable limits.
        """
        super(Robot, self).__init__(0.0, 0.0)
        # TODO make a robot builder/factory to abstract these sizes
        self._radius = 180e-3 / 2
        self.front_cut = self._radius * 0.7
        if max_speed is not None:
            self.max_speed = max_speed
            self.max_speed_dribbling = max_speed * 0.75
        if max_ang_speed is not None:
            self.max_ang_speed = max_ang_speed

        # ideally robot should inherit from a class that has an angle
        # and some geometry framework can use that angle
        self.angle = None
        self.speed = array((0.0, 0.0))
        self.acceleration = array((0.0, 0.0))
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

        # last skill, and tactic that was executed
        self.skill = None
        self.tactic = None

        # some properties
        self.can_kick = True

        self.is_touching = False
        self._has_touched = False
        self.is_last_toucher = False

        class Steppable(object):
            def step(self):
                pass

        self.current_tactic = Steppable()

        # update some components
        self.update((0.0, 0.0))

    def __eq__(self, other):
        return self.uuid == other.uuid

    def __ne__(self, other):
        return self.uuid != other.uuid

    def __str__(self):
        color = 'Blue' if self.color == Blue else 'Yellow' if self.color == Yellow else 'NoColor'
        return '<Robot {}:{} at {}>'.format(self.uid, color, super(Robot, self).__str__())

    def update(self, *args, **kwargs):
        """This is just a hook over the original function to cache some data."""
        super(Robot, self).update(*args, **kwargs)
        # TODO generate the actual body shape instead of a circle
        self._body = geom.Circle(self, self._radius)
        angle = self.angle or 0.0
        d = array((cos(angle), sin(angle)))
        self.kicker = geom.Point(array(self) + d * self.front_cut)

    @property
    def ball(self):
        return self.world.ball

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
    def is_goalie(self):
        return self.team.goalie == self.uid if self.team is not None else None

    @property
    def world(self):
        if self.team is not None:
            return self.team.world
        else:
            return None

    def is_enemy(self, robot):
        """Name says it all."""
        return self.team.color != robot.team.color

    @property
    def has_touched_ball(self):
        was_touching = self.is_touching
        self.is_touching = self.distance(self.ball) < self.radius + 2 * self.ball.radius
        if not self.is_touching and was_touching:
            self._has_touched = True
            return True
        return False

    @has_touched_ball.setter
    def has_touched_ball(self, value):
        self._has_touched = value

    def on_enemy_side(self):
        if self.enemy_goal is not None:
            return True if self.x * self.enemy_goal.x > 0 else False

    def on_ally_side(self):
        if self.enemy_goal is not None:
            return False if self.x * self.enemy_goal.x > 0 else True

    def step(self):
        if self._skill is not None:
            self._skill.step()


class Team(keydefaultdict):
    """This is basically a list of robots."""

    def __init__(self, color, robots=[], world=None):
        super(Team, self).__init__(partial(Robot, team=self), imap(lambda r: (r.pattern, r), robots))

        self.color = color
        self.world = world

        # team info attributes
        self.name = None
        self.score = None
        self.red_cards = None
        self.yellow_cards = None
        self.yellow_card_times = None
        self.timeouts = None
        self.timeout_time = None
        self._default_goalie = 0
        self._goalie = None

        # last play stepped on this team
        self.play = None

        # update robots' team
        for r in self.itervalues():
            r.team = self

    @property
    def goalie(self):
        return self._goalie or self._default_goalie

    @goalie.setter
    def goalie(self, goalie):
        self._goalie = goalie

    @property
    def default_goalie(self):
        return self._default_goalie

    @default_goalie.setter
    def default_goalie(self, goalie):
        self.default_goalie = goalie

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
        """active: True, only active; False, only inactive; None, both."""
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

    def best_indirect_positions(self, target=None, precision=6):
        """
        Discretizes points over the field (respecting a minimum border from the field,
        and without entering none of the defense areas), according to given precision.
        Searches for clear paths between initial position (ball), intermediate position,
        and the target.

        Returns a sorted list of tuples (Points that are closer to the target come
        first):
        [(point, distance_to_target), (point, distance_to_target), (point, distance_to_target), ...]
        """
        # TODO: aim for the best spot in the goal, not only to the middle of the enemy goal

        #t = self.team
        b = self.world.ball

        if target is None:
            target = self.enemy_goal

        candidate = []

        safety_margin = 2 * self[0].radius + 0.1

        # field params:
        f_l = self.world.length - self.world.defense_radius - safety_margin
        f_w = self.world.width - safety_margin

        # candidate points in the field range
        for x in linspace(-f_l / 2, f_l / 2, precision):
            for y in linspace(-f_w / 2, f_w / 2, precision - 2):
                pt = geom.Point(x, y)
                acceptable = True
                final_line = geom.Point(0, 0)
                for enemy in self.world.enemy_team(self.color).iterrobots():
                    # if the robot -> pt line doesn't cross any enemy body...
                    start_line = geom.Line(b, pt)
                    if not start_line.crosses(enemy.body):
                        final_line = geom.Line(pt, target)
                        # if the pt -> target line crosses any enemy body...
                        if final_line.crosses(enemy.body):
                            acceptable = False
                if acceptable:
                    candidate += [(pt, start_line.length + final_line.length)]
        if not candidate:
            #goal_point = self.enemy_goal
            return [(geom.Point(self.enemy_goal.x - sign(self.enemy_goal.x), self.enemy_goal.y), 1)]
        else:
            return sorted(candidate, key=lambda tup: tup[1])

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
        assert len(args) == 2
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
        self._area = None

    @property
    def penalty_line(self):
        """A line the robots must not advance on penalty on this goal."""
        return geom.Line(
            geom.Point(self.x - (sign(self.x) or 1) * (self.world.penalty_spot_distance + self.world.penalty_line_distance), -self.world.width / 2),
            geom.Point(self.x - (sign(self.x) or 1) * (self.world.penalty_spot_distance + self.world.penalty_line_distance), self.world.width / 2),
        )

    @property
    def penalty_stop(self):
        """A point where the ball should be on a penalty on this goal."""
        return geom.Point(array(self) - array(((sign(self.x) or 1) * (self.world.penalty_spot_distance), 0)))

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

    @property
    def is_blue(self):
        return self.world.blue_goal == self

    @property
    def is_yellow(self):
        return self.world.yellow_goal == self

    @property
    def area(self):
        if self._area:
            return self._area
        else:
            # Area of the goal + radius of the robots
            self._area = geom.Line([
                array(self) + array((0, self.world.defense_stretch / 2)),
                array(self) - array((0, self.world.defense_stretch / 2))
            ]).buffer(
                self.world.defense_radius +
                # Robot radius...
                180e-3 / 2
            )
            return self._area

    def point_outside_area(self, point):
        # TODO: Select the point better
        if point.within(self.area):
            r = point.distance(self.area.exterior)
            return point.buffer(r + 0.01).intersection(self.area.exterior).centroid
        return point


class Referee(object):

    class _Enum(object):
        @classmethod
        def _pretty(cls, value):
            for name in dir(cls):
                if not name.startswith('_'):
                    if getattr(cls, name) == value:
                        return name

    class Stage(_Enum):
        NormalFirstHalfPre = ref.NORMAL_FIRST_HALF_PRE
        NormalFirstHalf = ref.NORMAL_FIRST_HALF
        NormalHalfTime = ref.NORMAL_HALF_TIME
        NormalSecondHalfPre = ref.NORMAL_SECOND_HALF_PRE
        NormalSecondHalf = ref.NORMAL_SECOND_HALF
        ExtraTimeBreak = ref.EXTRA_TIME_BREAK
        ExtraFirstHalfPre = ref.EXTRA_FIRST_HALF_PRE
        ExtraFirstHalf = ref.EXTRA_FIRST_HALF
        ExtraHalfTime = ref.EXTRA_HALF_TIME
        ExtraSecondHalfPre = ref.EXTRA_SECOND_HALF_PRE
        ExtraSecondHalf = ref.EXTRA_SECOND_HALF
        PenaltyShootoutBreak = ref.PENALTY_SHOOTOUT_BREAK
        PenaltyShootout = ref.PENALTY_SHOOTOUT
        PostGame = ref.POST_GAME

    class Command(_Enum):
        Halt = ref.HALT
        Stop = ref.STOP
        NormalStart = ref.NORMAL_START
        ForceStart = ref.FORCE_START
        PrepareKickoffYellow = ref.PREPARE_KICKOFF_YELLOW
        PrepareKickoffBlue = ref.PREPARE_KICKOFF_BLUE
        PreparePenaltyYellow = ref.PREPARE_PENALTY_YELLOW
        PreparePenaltyBlue = ref.PREPARE_PENALTY_BLUE
        DirectFreeYellow = ref.DIRECT_FREE_YELLOW
        DirectFreeBlue = ref.DIRECT_FREE_BLUE
        IndirectFreeYellow = ref.INDIRECT_FREE_YELLOW
        IndirectFreeBlue = ref.INDIRECT_FREE_BLUE
        TimeoutYellow = ref.TIMEOUT_YELLOW
        TimeoutBlue = ref.TIMEOUT_BLUE
        GoalYellow = ref.GOAL_YELLOW
        GoalBlue = ref.GOAL_BLUE

    def __init__(self, world):
        self.world = world
        self.timestamp = None
        self.stage = None
        self.stage_time_left = None
        self.command = None
        self.command_timestamp = None

    @property
    def pretty_command(self):
        return self.Command._pretty(self.command)

    @property
    def pretty_stage(self):
        return self.Stage._pretty(self.stage)


class World(object):

    # default metric constants, may be overriden at
    # runtime, per instance or globally
    width = 4.0
    length = 6.0
    line_width = 0.01
    boundary_width = 0.25
    referee_width = 0.425
    center_radius = 0.5
    defense_radius = 0.5
    defense_stretch = 0.35
    free_kick_distance = 0.7
    penalty_spot_distance = 0.45
    penalty_line_distance = 0.35
    goal_width = 0.7
    goal_depth = 0.18
    goal_wall_width = 0.02

    def __init__(self, right_team=None, left_team=None):
        self.inited = False
        self.timestamp = 0

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
        self.right_goal = Goal(self, self.length / 2, 0.0)
        self.left_goal = Goal(self, -self.length / 2, 0.0)
        self.referee = None
        self.ball = Ball(self)

        # the referee
        self.referee = Referee(self)

    def switch_sides(self):
        self.right_team, self.left_team = self.left_team, self.right_team

    def has_clear_shot(self, point_to_kick):
        shot_line = geom.Line(self.ball, point_to_kick).buffer(self.ball.radius)
        for robot in self.iterrobots():
            if shot_line.crosses(robot.body):
                return False
        return True

    def has_clear_shot_from_position(self, kicker_position, point_to_kick):
        shot_line = geom.Line(kicker_position, point_to_kick)
        for robot in self.iterrobots():
            if shot_line.crosses(robot.body):
                return False
        return True

    def has_clear_pass(self, receiver):
        shot_line = geom.Line(self.ball, receiver)
        for robot in self.iterrobots():
            if shot_line.crosses(robot.body) and robot != receiver:
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
            return (not self.defense_area(color).intersection(body).is_empty)  # or abs(body.centroid.x) > abs(self.goal(color).x)
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

    def augmented_defense_area(self, robot, color):
        goal = self.goal(color)
        r = self.defense_radius
        s = self.defense_stretch
        l = (2 - sqrt(2)) * r
        return geometry.Polygon((
            (goal.x, r + s / 2),
            (goal.x - sign(goal.x) * (r - l), r + s / 2),
            (goal.x - sign(goal.x) * (r), r + s / 2 - l),
            (goal.x - sign(goal.x) * (r), l - r - s / 2),
            (goal.x - sign(goal.x) * (r - l), - r - s / 2),
            (goal.x, -r - s / 2),
            (goal.x, r + s / 2)
        ))
        #goal = self.goal(color)
        #gx, gy = goal.x, goal.y
        ##goal_width = self.goal_width
        #defense_area_radius = self.defense_radius
        #defense_area_stretch = self.defense_stretch
        #line_to_buffer = geom.Line([(gx, gy + defense_area_stretch / 2), (gx, gy - defense_area_stretch / 2)])
        #return line_to_buffer.buffer(defense_area_radius + robot.radius + 0.1)

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
        distance_robots_list = [(r.distance(point), r) for r in self.iterrobots(can_kick=can_kick, color=color)]
        if distance_robots_list:
            d, r = min(distance_robots_list)
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
