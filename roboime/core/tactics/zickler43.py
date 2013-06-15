from numpy import linspace
from itertools import groupby

from .. import Tactic
from ...utils.statemachine import Transition
from ..skills.drivetoball import DriveToBall
from ..skills.sampledkick import SampledKick
from ..skills.sampleddribble import SampledDribble
from ..skills.halt import Halt
from ...utils.geom import Point


class Zickler43(Tactic):
    """
    For more details see page 43 of the Zickler thesis.

    Ok, actually, no. This tactic is far from the original however
    the purpose is basically the same. This is an attacker. Main 
    differences from zickler thesis are that this tactic is deterministic,
    and that the minikick skill doesn't appear here.

    Somebody has to make goals, so, this is it, this will be
    the tactic that will make goals. And it will!
    """
    def __init__(self, robot, deterministic=True):
        self._lookpoint = robot.enemy_goal
        self.drive = DriveToBall(robot, lookpoint=self.lookpoint, deterministic=True)
        self.dribble = SampledDribble(robot, deterministic=deterministic, lookpoint=self.lookpoint, minpower=0.0, maxpower=1.0)
        self.goal_kick = SampledKick(robot, deterministic=deterministic, lookpoint=self.lookpoint, minpower=0.9, maxpower=1.0)
        self.wait = Halt(robot)

        super(Zickler43, self).__init__([robot], deterministic=deterministic, initial_state=self.drive, transitions=[
            Transition(self.drive, self.dribble, condition=lambda: self.drive.close_enough()),
            Transition(self.dribble, self.drive, condition=lambda: not self.dribble.close_enough()),
            Transition(self.dribble, self.goal_kick, condition=lambda: self.dribble.close_enough()),
            Transition(self.goal_kick, self.drive, condition=lambda: not self.goal_kick.close_enough()),
        ])

        self.max_hole_size = -1

    @property
    def lookpoint(self):
        return self._lookpoint

    @lookpoint.setter
    def lookpoint(self, point):
        self._lookpoint = point
        for state in [self.drive, self.dribble, self.goal_kick]:
            state.lookpoint = point

    def step(self):
        lookpoint = self.point_to_kick()
        if lookpoint is not None:
            self.lookpoint = lookpoint
        super(Zickler43, self).step()

    def point_to_kick(self):
        enemy_goal = self.robot.enemy_goal
        max_hole = []

        possible_points = [(y, self.world.has_clear_shot(Point(enemy_goal.x, y))) for y in linspace(enemy_goal.p2.y, enemy_goal.p1.y, 5)]

        for has_clear_shot, group in groupby(possible_points, lambda (point, has): has):
            if has_clear_shot:
                hole = list(group)
                if len(hole) > len(max_hole):
                    max_hole = hole

        if len(max_hole) != 0:
            y = (max_hole[0][0] + max_hole[-1][0]) / 2
            return Point(enemy_goal.x, y)
