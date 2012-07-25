"""
This module holds the base classes.
"""
from .utils import Particle

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


class Action(Particle):
    """An instance of this class determines what will a robot do."""

    def __init__(self, x, y, angle, kick=0, chipkick=0, dribble=0):
        self.robot = None
        self.x = x
        self.y = y
        self.angle = angle
        self.kick = kick
        self.chipkick = chipkick
        self.dribble = dribble

    @property
    def uid(self):
        return self.robot.uid

    @property
    def speeds(self):
        w = .1
        from math import cos, sin
        r = self.robot
        a = r.angle
        p = (self.x - r.x, self.y - r.y)
        px = p[0] * cos(a) - p[1] * sin(a)
        py = p[0] * sin(a) + p[1] * cos(a)
        return map(lambda i: w * i, [px, py, self.angle - a])


class Robot(Particle):
    """This class represents a robot, regardless of the team."""

    def __init__(self, uid, body=None, dribbler=None, kicker=None, wheels=[], battery=None):
        self.angle = None

        # basic
        self.uid = uid
        self.pattern = None
        self.team = None

        # components
        self.dribbler = dribbler
        self.kicker = kicker
        self.wheels = wheels
        self.battery = battery

        # action to be dispatched by a commander
        self._action = None

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, value):
        self._action = value
        self._action.robot = self

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


class Team(list):
    """This is basically a list of robots."""

    def __init__(self, color, robots=[]):
        super(Team, self).__init__(robots)

        self.color = color
        self.field = None

        # update robots' team
        for r in self:
            r.team = self

    def __getitem__(self, uid):
        for r in self:
            if r.uid == uid:
                return r
        else:
            r = Robot(uid)
            r.team = self
            self.append(r)
            return r

    def __setitem__(self, *args):
        #TODO: raise proper exception?
        raise IndexError('__setitem__ not allowed')

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


class Ball(Particle):
    """Well, a ball."""

    def __init__(self):
        self.radius = None


class Field(object):

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
        return self.right_team + self.left_team


