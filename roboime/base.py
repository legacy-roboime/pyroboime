"""
This module holds the base classes.
"""
from numpy import ndarray, isnan


class Partciple(ndarray):
    """Every object that has a position subclasses this class."""
    
    def __new__(cls, *args, **kwargs):
        self = ndarray.__new__(cls, shape=(3))
        self[0] = self[1] = self[2] = None
        return self

    @property
    def x(self):
        return self[0] if not isnan(self[0]) else None

    @x.setter
    def x(self, value):
        self[0] = value

    @property
    def y(self):
        return self[1] if not isnan(self[1]) else None

    @y.setter
    def y(self, value):
        self[1] = value

    @property
    def z(self):
        return self[2] if not isnan(self[2]) else None

    @z.setter
    def z(self, value):
        self[2] = value


class Component:
    """Use this class to build components such as kicker or dribbler"""
    
    def __init__(self):
        self.working = None
        self.active = None

    @property
    def broken(self):
        return not self.working if self.working is not None else None


class Robot(Partciple):
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


class Ball(Partciple):
    """Well, a ball."""
    
    def __init__(self):
        self.radius = None


class Goal(Partciple):

    def __init__(self):
        self.width = None
        self.depth = None
        self.wall_width = None


class Field:
    
    def __init__(self, right_team, left_team):
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

        # objects
        self.right_goal = Goal()
        self.right_team = None
        self.left_goal = Goal()
        self.left_team = None


