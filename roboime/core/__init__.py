"""
This is the core module that holds the base for Skills,
Tactics and Plays.
Might it be splitted?
"""
from ..utils.statemachine import State, Machine


class Skill(State):

    def __init__(self, robot, deterministic):
        super(Skill, self).__init__(deterministic)
        self.robot = robot

    @property
    def world(self):
        return self.robot.world

    @property
    def team(self):
        return self.robot.team

    @property
    def goal(self):
        return self.team.goal

    @property
    def ball(self):
        return self.world.ball

    def step(self):
        pass

    def busy(self):
        return False


class Tactic(Machine):

    def __init__(self, robots, deterministic, **kwargs):
        super(Tactic, self).__init__(deterministic, **kwargs)
        self.robots = robots

    @property
    def robot(self):
        return self.robots[0]

    @property
    def world(self):
        return self.robot.world

    @property
    def team(self):
        return self.robot.team

    @property
    def goal(self):
        return self.robot.goal

    @property
    def ball(self):
        return self.world.ball

    def step(self):
        pass


class Play(object):

    def __init__(self, team):
        self.team = team

    @property
    def world(self):
        return self.team.world

    @property
    def goal(self):
        return self.team.goal
