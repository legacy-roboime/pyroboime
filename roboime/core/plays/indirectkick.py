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
from .stop import Stop
from ..tactics.zickler43 import Zickler43
from ..skills.gotolooking import GotoLooking
from ..skills.sampledchipkick import SampledChipKick
from ...utils.statemachine import Machine as StateMachine, State, Transition


class IndirectKick(Stop, StateMachine):
    """
    Currently this play will extend StopReferee by performing an
    indirect kick by positioning a robot on a good spot and making
    a pass to it.
    """

    def __init__(self, team, verbose=False, **kwargs):
        super(IndirectKick, self).__init__(team, deterministic=True, **kwargs)
        #Stop.__init__(self, team, **kwargs)

        self.states = {
            'starting': State(True, name='Starting'),
            'touched': State(True, name='Touched'),
            'go_position': State(True, name='Go to position'),
            'pass': State(True, name='Pass'),
            'end': State(True, name='End')
        }

        transitions = [
            Transition(from_state=self.states['starting'], to_state=self.states['end'], condition=lambda: self.passer is None),
            Transition(from_state=self.states['starting'], to_state=self.states['go_position'], condition=lambda: self.passer is not None),
            # TODO: Parametrize this
            Transition(from_state=self.states['go_position'], to_state=self.states['pass'], condition=lambda: self.receiver.distance(self.best_position) < 0.2),
            Transition(from_state=self.states['pass'], to_state=self.states['touched'], condition=lambda: self.passer.is_last_toucher),
            Transition(from_state=self.states['touched'], to_state=self.states['end'], condition=lambda: not self.passer.is_last_toucher),
        ]
        StateMachine.__init__(self, deterministic=True, initial_state=self.states['starting'], transitions=transitions)

        self.players = {}
        self.team = team
        self.receiver = None
        self.passer = None
        self.tactics_factory.update({
            'receiver': lambda robot: GotoLooking(robot, lookpoint=self.world.ball),
            'passer': lambda robot: SampledChipKick(robot, receiver=self.receiver, lookpoint=self.receiver),
            'zickler': lambda robot: Zickler43(robot),
        })
        self.best_position = None
        self.verbose = verbose

    def restart(self):
        self.current_state = self.states['starting']
        self.receiver = None
        self.passer = None

    @property
    def goalkeeper(self):
        l = [r for r in self.team if r.uid == self.goalie]
        if l:
            return l[0]
        return None

    def setup_tactics(self):
        Stop.setup_tactics(self)
        if self.verbose:
            print self.current_state
        if self.current_state == self.states['starting']:
            self.best_position = self.team.best_indirect_positions()[0][0]
            robots_closest_to_ball = self.team.closest_robots_to_ball()
            # TODO: Think of a better name
            robots_closest_to_bathtub = self.team.closest_robots_to_point(point=self.best_position)

            for robot in self.team:
                if robot.uid == self.goalie:
                    robots_closest_to_ball.remove(robot)
                    robots_closest_to_bathtub.remove(robot)
                    break

            self.receiver = self.passer = None
            if robots_closest_to_bathtub:
                self.receiver = robots_closest_to_bathtub[0]

            for robot in robots_closest_to_ball[:]:
                if robot == self.receiver:
                    robots_closest_to_ball.remove(robot)
                    break

            if robots_closest_to_ball:
                self.passer = robots_closest_to_ball[0]

            #for robot in self.team:
            #    robot.current_tactic = Steppable()

        elif self.current_state == self.states['go_position']:
            self.players[self.receiver.uid]['receiver'].target = self.best_position
            self.receiver.current_tactic = self.players[self.receiver.uid]['receiver']

            #for robot in self.team:
            #    if robot != self.receiver:
            #        robot.current_tactic = Steppable()

        elif self.current_state == self.states['pass']:
            self.best_position = self.team.best_indirect_positions()[0][0]

            self.players[self.passer.uid]['passer'].receiver = self.receiver
            self.players[self.passer.uid]['passer'].lookpoint = self.receiver
            self.passer.current_tactic = self.players[self.passer.uid]['passer']

            self.players[self.receiver.uid]['receiver'].target = self.best_position
            self.receiver.current_tactic = self.players[self.receiver.uid]['receiver']
            #for robot in self.team:
            #    if robot != self.passer and robot != self.receiver:
            #        robot.current_tactic = Steppable()

        elif self.current_state == self.states['touched']:
            robots_closest_to_ball = self.team.closest_robots_to_ball()
            try:
                robots_closest_to_ball.remove(self.goalkeeper)
            except ValueError:
                pass
            try:
                robots_closest_to_ball.remove(self.passer)
            except ValueError:
                pass

            attacker = robots_closest_to_ball[0]
            attacker.current_tactic = self.players[attacker.uid]['zickler']

            self.players[self.receiver.uid]['receiver'].target = self.best_position
            self.receiver.current_tactic = self.players[self.receiver.uid]['receiver']

            #for robot in self.team:
            #    if robot != attacker and robot != self.receiver:
            #        robot.current_tactic = Steppable()
        #else:
        #    for robot in self.team:
        #        robot.current_tactic = Steppable()

        # Executes state machine transitions
        self.execute()
