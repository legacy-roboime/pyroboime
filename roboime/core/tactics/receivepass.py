from numpy import linspace
from itertools import groupby

from .. import Tactic
from ...utils.statemachine import Transition
from ..skills.drivetoball import DriveToBall
from ..skills.sampledkick import SampledKick
from ..skills.sampleddribble import SampledDribble
from ..skills.halt import Halt
from ...utils.geom import Point

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

    #point_to_kick = Zickler43.point_to_kick.im_func

    def __init__(self, robot, companion_tactic, deterministic=True):
        self._lookpoint = None
        self._robot = robot
        self.companion_tactic = companion_tactic
        #self.drive_to_position = DriveTo(robot, lookpoint=self.lookpoint, deterministic=True, avoid_collisions=True)
        self.wait = Halt(robot)
        
        super(ExecutePass, self).__init__(robot, deterministic, initial_state=self.drive, transitions=[

        ])

    def ready(self):
        return True
