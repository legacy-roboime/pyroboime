#
# Copyright (C) 2013 RoboIME
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
from numpy import linspace
from itertools import groupby

from .. import Tactic
from ...utils.statemachine import Transition
from ..skills.drivetoball import DriveToBall
from ..skills.sampledkick import SampledKick
from ..skills.sampledchipkick import SampledChipKick
from ..skills.sampleddribble import SampledDribble
from ..skills.halt import Halt
from ..skills.kickto import KickTo
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
    class Kicker(object):
        def __init__(self):
            self.kicker = Point(0, 0)

    class CompanionCube(object):
        def __init__(self, robot):
            self._robot = ExecutePass.Kicker()

        @property
        def robot(self):
            return self._robot

        @property
        def ready(self):
            return True

    def __init__(self, robot, companion_tactic=None, deterministic=True):
        self.done = False
        self._robot = robot
        self.companion = companion_tactic or ExecutePass.CompanionCube(self.robot)

        self.drive = DriveToBall(robot, lookpoint=lambda: self.companion.robot, deterministic=True, avoid_collisions=True)
        self.dribble = SampledDribble(robot, deterministic=deterministic, lookpoint=lambda: self.companion.robot, minpower=0.0, maxpower=1.0)
        self.kick = KickTo(robot, lookpoint=lambda: self.companion.robot.kicker, minpower=0.9, maxpower=1.0)
        #self.chip_kick = SampledChipKick(robot, deterministic=deterministic, lookpoint=lambda: self.companion.robot.kicker, receiver=self.companion.robot.kicker, minpower=0.9, maxpower=1.0)

        super(ExecutePass, self).__init__(robot, deterministic, initial_state=self.drive, transitions=[
            Transition(self.drive, self.dribble, condition=lambda: self.drive.close_enough()),
            Transition(self.dribble, self.drive, condition=lambda: not self.dribble.close_enough()),
            Transition(self.dribble, self.kick, condition=lambda: self.dribble.close_enough() and self.companion.ready),
            #Transition(self.dribble, self.chip_kick, condition=lambda: self.dribble.close_enough() and not self.world.has_clear_pass(self.companion.robot) and self.companion.ready),
            Transition(self.kick, self.drive, condition=lambda: not self.kick.good_position(), callback=self.set_passed),
            #Transition(self.chip_kick, self.drive, condition=lambda: not self.chip_kick.close_enough(), callback=self.set_passed),
            #Transition(self.kick, self.chip_kick, condition=lambda: self.kick.good_position() and not self.world.has_clear_pass(self.companion.robot)),
            #Transition(self.chip_kick, self.kick, condition=lambda: not self.chip_kick.close_enough() and self.world.has_clear_pass(self.companion.robot)),
        ])

    def set_passed(self):
        self.done = True
