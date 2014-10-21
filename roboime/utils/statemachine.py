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
from random import random


class State(object):

    def __init__(self, deterministic, name=None, **kwargs):
        #super(State, self).__init__(**kwargs)
        super(State, self).__init__()

        if name is not None:
            self.name = name
        self.deterministic = deterministic


class Transition(object):

    def __init__(self, from_state, to_state, probability=1.0, condition=None, callback=lambda: None, **kwargs):
        """
        This class can be used in two ways:
        - subclass it and redefine the condition method
        - pass a condition function while constructing
        """
        super(Transition, self).__init__(**kwargs)

        self.from_state = from_state
        self.to_state = to_state
        self.probability = probability
        self._condition = condition
        self.callback = callback

    def condition(self):
        if self._condition is not None:
            return self._condition()


class Machine(object):

    def __init__(self, deterministic, initial_state=None, transitions=[], **kwargs):
        super(Machine, self).__init__(**kwargs)

        self.deterministic = deterministic
        self.initial_state = initial_state
        #self.final_state = final_state
        self.current_state = initial_state
        self.transitions = transitions

    def reset(self):
        self.current_state = self.initial_state

    def execute(self):
        possible_transitions = [t for t in self.transitions if t.from_state is self.current_state and t.condition()]
        if self.deterministic:
            if possible_transitions:
                self.current_state = possible_transitions[0].to_state
                possible_transitions[0].callback()
        else:
            total_prob = sum(t.probability for t in possible_transitions)
            rand_prob = total_prob * random()
            tmp_prob = 0.0
            for t in possible_transitions:
                tmp_prob += t.probability
                if rand_prob < tmp_prob:
                    self.current_state = t.to_state
                    t.callback()
                    break
