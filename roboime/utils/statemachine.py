from random import random


class State(object):
    def __init__(self, deterministic):
        self.deterministic = deterministic
        self.transitions = []

    def busy(self):
        pass


class Transition(object):
    def __init__(self, from_state, to_state, probability=1.0):
        self.from_state = from_state
        self.to_state = to_state
        self.probability = probability

    def condition():
        pass


class Machine(object):
    def __init__(self, deterministic, states=[], initial_state=None, final_state=None):
        self.deterministic = deterministic
        self.states = states
        self.initial_state = initial_state
        self.final_state = final_state
        # set current state
        self.reset()

    def reset(self):
        self.current_state = self.initial_state

    def busy(self):
        return self.current_state.busy()

    def execute(self):
        possible_transitions = [t for t in self.current_state.transitions if t.condition()]
        if self.deterministic:
            if possible_transitions:
                self.current_state = possible_transitions[0].to_state
        else:
            total_prob = sum(t.probability for t in possible_transitions)
            rand_prob = total_prob * random()
            tmp_prob = 0.0
            for t in possible_transitions:
                tmp_prob += t.probability
                if rand_prob < tmp_prob:
                    self.current_state = t.to_state
                    break
