#
# Copyright (C) 2013-2015 RoboIME
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
from .indirectkick import IndirectKick
from ...base import Referee
from ...utils.geom import Point


State = Referee.State


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
    def __init__(self, main_play, verbose=True):
        super(ObeyReferee, self).__init__(main_play.team)

        # plays
        self.main_play = main_play
        self.stop = Stop(self.team)
        self.halt = Halt(self.team)
        self.penalty = Penalty(self.team)
        self.penalty_defend = PenaltyDefend(self.team)
        self.indirect_kick = IndirectKick(self.team)  # AutoRetaliate(self.team) # Ifrit(self.team, allowed_to_kick=False) #

    def select_play(self):
        state = self.world.referee.state

        self.main_play.clean()

        if state == State.stop:
            self.indirect_kick.reset()
            return self.stop

        if state == State.normal:
            return self.main_play

        if state == State.avoid:
            self.main_play.avoid_id = self.world.referee.more_info
            return self.main_play

        if state == State.pre_kickoff_player:
            # TODO: get closer to kick, don't act like Stop
            return self.stop

        if state == State.kickoff_player:
            return self.main_play

        if state == State.indirect_player:
            return self.indirect_kick

        if state == State.direct_player:
            # TODO: we can do better than this
            return self.main_play

        if state == State.pre_penalty_player:
            # Sets up the penalty kicker on the penalty position
            self.penalty.is_last_toucher = False
            self.penalty.ready = False
            return self.penalty

        if state == State.penalty_player:
            # After the penalty kicker reaches its position, it actually kicks
            self.penalty.ready = True
            return self.penalty

        if state == State.pre_kickoff_opponent or state == State.kickoff_opponent:
            # TODO: take better defensive position
            return self.stop

        if state == State.indirect_opponent or state == State.direct_opponent:
            # TODO: take better defensive position
            return self.stop

        if state == State.pre_penalty_opponent or state == State.penalty_opponent:
            return self.penalty_defend

    def step(self):
        play = self.select_play()
        return play.step()
