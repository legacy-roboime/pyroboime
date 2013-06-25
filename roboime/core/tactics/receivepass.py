from numpy import linspace
from itertools import groupby

from .. import Tactic
from ...utils.statemachine import Transition
from ..skills.drivetoball import DriveToBall
from ..skills.sampledkick import SampledKick
from ..skills.sampleddribble import SampledDribble
from ..skills.halt import Halt
from ...utils.geom import Point
from ..skills.gotolooking import GotoLooking

class ReceivePass(Tactic):
    '''
    This tactic has the objective of receiving the ball from 
    another robot in the field. This side is a bit more complicated:
    discretize the positions in a circle around the robot, see which
    one has the best clear shot (ordered by closeness to the target 
    goal) and move to that position with the ball as a lookpoint.

    This tactic is designed to work along a ExecutePass tactic
    (or any other tactic that implements its methods). This is 
    so that one tactic can signal to the other when it is ready,
    while obscuring details such as which robot is doing what.
    '''
    
    class CompanionCube(object):
        def __init__(self, robot):
            self._robot = None

        @property
        def robot(self):
            return self._robot

        @property
        def ready(self):
            return True

    def __init__(self, robot, point=None, companion=None, deterministic=True):
        self._robot = robot
        self._point = point or self.robot
        self.companion = companion or self.CompanionCube(self.robot)
        
        self.goto = GotoLooking(self.robot, target=self.point, lookpoint=lambda: self.companion.robot.kicker)

        super(ReceivePass, self).__init__(robot, deterministic, initial_state=self.goto, transitions=[])

    @property
    def point(self):
        return self._point

    @point.setter
    def point(self, value):
        self._point = value

    def ready(self):
        print self.robot.distance(self.point) < 0.2
        return self.robot.distance(self.point) < 0.2
