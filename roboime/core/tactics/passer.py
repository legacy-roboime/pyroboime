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
from time import time

from .. import Tactic
from ...utils.statemachine import Transition
from ..skills.drivetoball import DriveToBall
from ..skills.kickto import KickTo
from ..skills.gotolooking import GotoLooking


class Passer(Tactic):
    """
    This tactic will drive the robot close to the ball and pass it
    to a given mate.

    .. dot:: passer.png

        digraph passer {
            DriveToBall -> KickTo;
            KickTo -> DriveToBall;
        }

    """

    def __init__(self, robot):
        self._robot = robot
        self._lookpoint = None
        self.drive = DriveToBall(
            robot,
            name='Get the Ball',
            lookpoint=lambda: self.lookpoint,
            deterministic=True,
        )
        self.kick = KickTo(
            robot,
            name='Pass!',
            lookpoint=lambda: self.lookpoint,
            minpower=0.1,
            maxpower=0.5,
        )
        self.wait = GotoLooking(
            robot,
            name='Wait',
            target=robot,
            lookpoint=robot.world.ball
        )
        self.wait.timeout = 2.0 # in seconds
        self.wait.last_time = time()
        def update_last_time():
            self.wait.last_time = time()
        super(Passer, self).__init__(
            robot,
            initial_state=self.drive,
            transitions=[
                Transition(
                    self.drive,
                    self.kick,
                    condition=lambda: self.drive.close_enough(),
                    callback=lambda: self.kick.save_ball_pos(),
                ),
                Transition(
                    self.kick,
                    self.wait,
                    condition=lambda: self.kick.ball_kicked(),
                    callback=update_last_time,
                ),
                Transition(
                    self.kick,
                    self.drive,
                    condition=lambda: self.kick.bad_position(),
                ),
                Transition(
                    self.wait,
                    self.drive,
                    condition=lambda: time() - self.wait.last_time > self.wait.timeout,
                ),
            ],
        )

    @property
    def lookpoint(self):
        if callable(self._lookpoint):
            return self._lookpoint() or self.robot.enemy_goal
        else:
            return self._lookpoint or self.robot.enemy_goal

    @lookpoint.setter
    def lookpoint(self, p):
        self._lookpoint = p
