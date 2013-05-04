"""
This module holds the base classes.
"""
from itertools import imap
from collections import defaultdict
from functools import partial

from .utils import geom

Yellow = 'yellow'
Blue = 'blue'


class Component(object):
    """Use this class to build components such as kicker or dribbler"""

    def __init__(self):
        self.working = None
        self.active = None

    @property
    def broken(self):
        return not self.working if self.working is not None else None


class Action(geom.Point):
    """An instance of this class determines what will a robot do."""

    def __init__(self, robot):
        geom.Point.__init__(self)
        self.robot = robot
        self.x = None
        self.y = None
        self.angle = None
        self.kick = None
        self.chipkick = None
        self.dribble = None
        self.speed = None

    @property
    def target(self):
        return self.x, self.y, self.angle

    def __nonzero__(self):
        """This is used for implicit bool conversion, which answers if the action does something."""
        return not (self.x is None or self.y is None or self.angle is None)

    @target.setter
    def target(self, t):
        self.x, self.y, self.angle = t if t is not None else (None, None, None)

    @property
    def uid(self):
        return self.robot.uid

    @property
    def color(self):
        return self.robot.color

    @property
    def speeds(self):
        s = self.speed or 0.5
        #TODO: implement some PID, should this be really here?
        if not self:
            return (0.0, 0.0, 0.0)
        from .utils.mathutils import cos, sin
        x, y, a = self.target
        r = self.robot
        #import pudb; pudb.set_trace()
        ra = r.angle
        va = 0.2 * (a - ra)
        vx, vy = x - r.x, y - r.y
        vx, vy = vx * cos(ra) + vy * sin(ra), vy * cos(ra) - vx * sin(ra)
        return tuple(map(lambda t: s * t, (vx, vy, va)))


class Robot(geom.Circle):

    def __init__(self, uid, body=None, dribbler=None, kicker=None, wheels=[], battery=None, team=None):
        """This class represents a robot, regardless of the team."""
        super(Robot, self).__init__()

        # ideally robot should inherit from a class that has an angle
        # and some geometry framework can use that angle
        self.angle = None

        # basic
        self.uid = uid
        self.pattern = None
        self.team = team

        # components
        self.dribbler = dribbler
        self.kicker = kicker
        self.wheels = wheels
        self.battery = battery

        # action to be dispatched by a commander
        self._action = Action(self)

        # skill that will be executed
        self._skill = None

    @property
    def action(self):
        return self._action

    @property
    def height(self):
        return self.body.height if self.body else None

    @property
    def radius(self):
        return self.body.radius if self.body else None

    @property
    def color(self):
        if self.team is not None:
            return self.team.color
        else:
            return None

    @property
    def field(self):
        if self.team is not None:
            return self.team.field
        else:
            return None

    @property
    def skill(self):
        return self._skill

    @skill.setter
    def skill(self, nskill):
        nskill._robot = self
        self._skill = nskill

    def step(self):
        if self._skill is not None:
            self._skill.step()


class Team(defaultdict):
    """This is basically a list of robots."""

    def __init__(self, color, robots=[]):
        super(Team, self).__init__(partial(Robot, team=self), imap(lambda r: (r.pattern, r), robots))
        #super(Team, self).__init__(imap(lambda r: (r.uid, r), robots))

        self.color = color
        self.field = None

        # update robots' team
        for r in self.itervalues():
            r.team = self

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        else:
            val = self[key] = self.default_factory(key)
            return val

    #def __getitem__(self, uid):
    #    for r in self:
    #        if r.uid == uid:
    #            return r
    #    else:
    #        r = Robot(uid)
    #        r.team = self
    #        self.append(r)
    #        return r

    #def __setitem__(self, *args):
    #    #TODO: raise proper exception?
    #    raise IndexError('__setitem__ not allowed')

    @classmethod
    def blue(cls, *args, **kwargs):
        return cls(Blue, *args, **kwargs)

    @classmethod
    def yellow(cls, *args, **kwargs):
        return cls(Yellow, *args, **kwargs)

    @property
    def is_blue(self):
        return self.color == Blue

    @property
    def is_yellow(self):
        return self.color == Yellow

    def iterrobots(self):
        for r in self.itervalues():
            #TODO put active condition
            yield r

    def __iter__(self):
        return self.iterrobots()


class Ball(geom.Circle):
    """Well, a ball."""

    def __init__(self):
        super(Ball, self).__init__()
        self.x = 0
        self.y = 0


class World(object):

    def __init__(self, right_team=Team.yellow(), left_team=Team.blue()):
        # metric constants
        self.width = None
        self.length = None
        self.line_width = None
        self.boundary_width = None
        self.referee_width = None
        self.center_radius = None
        self.defense_radius = None
        self.defense_stretch = None
        self.free_kick_distance = None
        self.penalty_spot_distance = None
        self.penalty_line_distance = None
        self.goal_width = None
        self.goal_depth = None
        self.goal_wall_width = None

        # objects
        self.right_team = right_team
        self.left_team = left_team
        self.referee = None
        self.ball = Ball()

    def switch_sides(self):
        self.right_team, self.left_team = self.left_team, self.right_team

    @property
    def yellow_team(self):
        if self.right_team.color == Yellow:
            return self.right_team
        elif self.left_team.color == Yellow:
            return self.left_team
        else:
            raise Exception

    @property
    def blue_team(self):
        if self.right_team.color == Blue:
            return self.right_team
        elif self.left_team.color == Blue:
            return self.left_team
        else:
            raise Exception

    @property
    def robots(self):
        return list(self.iterrobots())

    def iterrobots(self):
        """W.iterrobots() -> an iterator over the robots of the world W."""
        for t in (self.right_team, self.left_team):
            for r in t.iterrobots():
                yield r

    def iterobjects(self):
        """W.iterobjects() -> an iterator over the objects of the world W."""
        yield self.ball
        for t in (self.right_team, self.left_team):
            for r in t.iterrobots():
                yield r

    def __iter__(self):
        return self.iterobjects()

