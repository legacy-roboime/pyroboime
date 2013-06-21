from numpy import linspace
from itertools import groupby

from .. import Tactic
from ...utils.statemachine import Transition
from ..skills.drivetoball import DriveToBall
from ..skills.sampledkick import SampledKick
from ..skills.sampleddribble import SampledDribble
from ..skills.halt import Halt
from ...utils.geom import Point

class ExecutePass(Tactic):
    '''
    This tactic has the objective of passing the ball to another
    robot in the field. This is the simpler side of the pass:
    aim for the other robot, then kick/chip the ball to him once
    its companion ReceivePass tactic is ready. It is very similar
    to the Zickler43 tactic in that respect.

    This tactic is designed to work along a ReceivePass tactic
    (or any other tactic that implements its methods). This is 
    so that one tactic can signal to the other when it is ready,
    while obscuring details such as which robot is doing what.
    '''
    
    def __init__(self, robot, companion_tactic, deterministic=True):
        self._lookpoint = None
        self._robot = robot
        self.companion_tactic = companion_tactic
        self.drive = DriveToBall(robot, lookpoint=self.lookpoint, deterministic=True, avoid_collisions=True)
        self.dribble = SampledDribble(robot, deterministic=deterministic, lookpoint=self.lookpoint, minpower=0.0, maxpower=1.0)
        self.kick = SampledKick(robot, deterministic=deterministic, lookpoint=self.lookpoint, minpower=0.9, maxpower=1.0)
        self.chip_kick = SampledChipKick(robot, deterministic=deterministic, lookpoint=self.lookpoint, minpower=0.9, maxpower=1.0)
        self.wait = Halt(robot)

        super(ExecutePass, self).__init__(robot, deterministic, initial_state=self.drive, transitions=[
        ])
