"""
This module holds the base classes.
"""


class Partciple:
    """Every object that has a position subclasses this class."""
    #TODO: math this
    
    def __init__(self):
        self.pos = [None, None, None]
        self.radius = None

    @property
    def x(self):
        return self.pos[0]

    @x.setter
    def x(self, pos):
        self.pos[0] = pos

    @property
    def y(self):
        return self.pos[1]

    @y.setter
    def y(self, pos):
        self.pos[1] = pos

    @property
    def z(self):
        return self.pos[2]

    @z.setter
    def z(self, pos):
        self.pos[2] = pos


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
        super().__init__()

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
        super().__init__(robots)

        self.color = color
        self.field = None

        # update robots' team
        for r in self:
            r.team = self


class Ball(Partciple):
    """Well, a ball."""
    
    def __init__(self):
        super().__init__()
        self.radius = None


class Goal:
    pass


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
        self.right_goal = None
        self.right_team = None
        self.left_goal = None
        self.left_team = None


