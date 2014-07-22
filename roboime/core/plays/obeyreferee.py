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
from numpy.linalg import norm

from .. import Play
from .stop import Stop
from .halt import Halt
from .penalty import Penalty
from .penaltydefend import PenaltyDefend
from .ifrit import Ifrit
from .indirectkick import IndirectKick
from .autoretaliate import AutoRetaliate
from ...base import Referee, Blue, Yellow
from ...utils.geom import Point

Command = Referee.Command
TOLERANCE = 0.15


class ObeyReferee(Play):
    """
    On normal tournament play, actions should be chosen according to
    referee commands. This (and other possible referee play variants)
    is the only play that should read from referee commands.

    It switches the appropriate plays for each ocasion, and receives one
    main play as a parameter: the play we'll be using to actually play
    the game on normal start/forced start situations.
    """

    # TODO: Implement this as a state machine variant (states as input, transitions as output).
    def __init__(self, play, verbose=True):
        super(ObeyReferee, self).__init__(play.team)
        self.play = play
        self.stop = Stop(self.team)
        self.halt = Halt(self.team)
        self.penalty_us = Penalty(self.team)
        self.penalty_them = PenaltyDefend(self.team)
        self.indirect_kick = IndirectKick(self.team)  # AutoRetaliate(self.team) # Ifrit(self.team, allowed_to_kick=False) #
        self.referee = self.world.referee
        self.command = self.referee.command
        self.last_command = Command.Halt
        self.last_ball = Point(self.world.ball)
        self.verbose = verbose
        self.halt = Halt(self.team)

    def step(self):
        self.first_time = False
        if self.command != self.referee.command:
            self.last_command = self.command
            self.command = self.referee.command
            self.last_ball = Point(self.ball)
            self.first_time = True
        ball_distance = self.ball.distance(self.last_ball)

        if self.verbose:
            pass

        if ((self.command == Command.DirectFreeYellow and self.team.color == Yellow) or
                (self.command == Command.DirectFreeBlue and self.team.color == Blue)):
            self.play.step()

        elif ((self.command == Command.PreparePenaltyYellow and self.team.color == Yellow) or
                (self.command == Command.PreparePenaltyBlue and self.team.color == Blue)):
            # Sets up the penalty kicker on the penalty position
            self.penalty_us.is_last_toucher = False
            self.penalty_us.ready = False
            self.penalty_us.step()

        elif (self.command == Command.NormalStart and
                ((self.last_command == Command.PreparePenaltyYellow and self.team.color == Yellow) or
                (self.last_command == Command.PreparePenaltyBlue and self.team.color == Blue))):
            # After the penalty kicker reaches its position, it actually kicks
            self.penalty_us.ready = True
            self.penalty_us.step()

            if self.penalty_us.attacker.is_last_toucher:
                self.last_command = Command.NormalStart

        elif ((self.command == Command.PreparePenaltyYellow and self.team.color == Blue) or
              (self.command == Command.PreparePenaltyBlue and self.team.color == Yellow)):
            self.penalty_them.step()

        elif (self.command == Command.NormalStart and
                ((self.last_command == Command.PreparePenaltyYellow and self.team.color == Blue) or
                (self.last_command == Command.PreparePenaltyBlue and self.team.color == Yellow))):
            # TODO: Should I put the ball's speed back here?
            if ball_distance > TOLERANCE:
                self.play.step()
                self.last_command = Command.NormalStart
            else:
                self.penalty_them.step()

        elif ((self.command == Command.DirectFreeBlue and self.team.color == Yellow) or
                (self.command == Command.DirectFreeYellow and self.team.color == Blue) or
                (self.command == Command.IndirectFreeBlue and self.team.color == Yellow) or
                (self.command == Command.IndirectFreeYellow and self.team.color == Blue) or
                (self.command == Command.NormalStart and
                (self.last_command == Command.PrepareKickoffYellow and self.team.color == Blue) or
                (self.last_command == Command.PrepareKickoffBlue and self.team.color == Yellow))):
            if norm(self.world.ball.speed) > TOLERANCE or ball_distance > TOLERANCE:
                self.play.step()
            else:
                self.stop.step()

        elif ((self.command == Command.IndirectFreeBlue and self.team.color == Blue) or
                (self.command == Command.IndirectFreeYellow and self.team.color == Yellow)):
            if self.first_time:
                pass
                #self.indirect_kick.reset()

            #print "Has passed: ", self.indirect_kick.has_passed
            if True:  # self.indirect_kick.has_passed:
                self.play.step()
            else:
                self.indirect_kick.step()
            #self.play.step()

        elif self.command in [Command.PrepareKickoffYellow, Command.PrepareKickoffBlue, Command.Stop, Command.TimeoutYellow, Command.TimeoutBlue]:
            self.stop.step()

        elif self.command == Command.Halt:
            self.halt.step()

        elif (self.command == Command.NormalStart and
                ((self.last_command == Command.PrepareKickoffYellow and self.team.color == Yellow) or
                (self.last_command == Command.PrepareKickoffBlue and self.team.color == Blue))):
            self.play.step()
        else:
            self.play.step()
