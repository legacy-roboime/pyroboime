"""
This module holds the base classes.
"""


class Robot:
    """
    This class represents a robot, regardless of the team.
    """

    def __init__(self):
        # identification
        self.id = None
        self.pattern = None
        self.color = None
        # components
        self.dribbler = None
        self.kicker = None
        self.wheels = []
        self.battery = None


class Team:
    pass


class Ball:
    pass


class Field:
    pass


