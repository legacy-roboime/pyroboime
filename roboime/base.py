"""
This module holds the base classes.
"""
from .utils import Particle


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
        self.goal_width = None
        self.goal_depth = None
        self.goal_wall_width = None

        # objects
        self.right_team = None
        self.left_team = None
        self.referee = None


