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
from .. import Tactic
from ...utils.statemachine import Transition
from ..skills.drivetoball import DriveToBall
from ..skills.kickto import KickTo


class Striker(Tactic):
    """
    Strike, strike, strike, get to the ball and strike.

    .. dot:: striker.png

        digraph striker {
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
            name='Kick!',
            lookpoint=lambda: self.lookpoint,
            minpower=0.9,
            maxpower=1.0,
        )

        super(Striker, self).__init__(
            robot,
            initial_state=self.drive,
            transitions=[
                Transition(
                    self.drive,
                    self.kick,
                    condition=lambda: self.drive.close_enough(),
                ),
                Transition(
                    self.kick,
                    self.drive,
                    condition=lambda: self.kick.bad_position(),
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
