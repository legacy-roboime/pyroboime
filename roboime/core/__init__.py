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
"""
This is the core module that holds the base for Skills,
Tactics and Plays.
Might it be splitted?
"""
from ..utils.statemachine import State, Machine
from ..utils import keydefaultdict
from ..utils.log import Log


class Steppable(object):

    name = None

    def __init__(self, *args, **kwargs):
        # the following is not the same as doing
        # >>> self.name = kwargs.get('name')
        # because the above will turn name into an instance
        # property, and overwrite it if defined as a class member
        if 'name' in kwargs and kwargs['name'] is not None:
            self.name = kwargs.pop('name')
        # continue the chain of inheritance init
        super(Steppable, self).__init__(*args, **kwargs)
        self.log = Log('core')
        #try:
        #    super(Steppable, self).__init__(*args, **kwargs)
        #except TypeError:
        #    pass

    def __str__(self):
        return self.name or self.__class__.__name__

    def step(self):
        """This method must be implemented to add some logic."""
        raise NotImplementedError


class Dummy(Steppable):
    """Use this class if you want a Steppable that does nothing."""

    def step(self):
        pass


class Skill(Steppable, State):

    def __init__(self, robot, deterministic, **kwargs):
        super(Skill, self).__init__(deterministic, **kwargs)
        self.robot = robot
        self.params = keydefaultdict.keydefaultdict(lambda x: None)

    @property
    def world(self):
        return self.robot.world

    @property
    def team(self):
        return self.robot.team

    @property
    def enemy_team(self):
        return self.team.enemy_team

    @property
    def goal(self):
        return self.team.goal

    @property
    def ball(self):
        return self.world.ball

    def _step(self):
        """This method must be implemented to add some logic."""
        raise NotImplementedError

    def step(self):
        """One should not override this method, this is the public api, which wraps around _step"""
        self._step()
        self.robot.skill = self

    def mark_skill(self):
        self.robot.skill = self
        for param in self.params.iterkeys:
            pvalue = getattr(self, param)
            self.params[param] = pvalue


class Tactic(Steppable, Machine):

    def __init__(self, robot, deterministic, **kwargs):
        super(Tactic, self).__init__(deterministic, **kwargs)
        self._robot = robot

    @property
    def robot(self):
        return self._robot

    @property
    def world(self):
        return self.robot.world

    @property
    def team(self):
        return self.robot.team

    @property
    def enemy_team(self):
        return self.team.enemy_team

    @property
    def goal(self):
        return self.robot.goal

    @property
    def ball(self):
        return self.world.ball

    def _step(self):
        """If not overriden this method will call self.execute() from MachineState."""
        if self.current_state is not None:
            self.current_state.step()
        self.execute()

    def step(self):
        """One should not override this method, this is the public api, which wraps around _step"""
        self._step()
        self.robot.tactic = self


class Play(Steppable):

    def __init__(self, team, **kwargs):
        """
        When constructing a derived play, keep in mind tactics_factory is a dictionary
        of lambda expressions that generate a steppable for a given robot.

        DO NOT overwrite the tactics_factory of your base play under any circumstances,
        under penalty of breaking the base play. Use tactics_factory.update(new_factory)
        instead. Remember to not use any keys already in your base factory.
        """
        super(Play, self).__init__(**kwargs)
        self.team = team
        self.tactics_factory = {}
        self.players = {}

    @property
    def enemy_team(self):
        return self.team.enemy_team

    @property
    def world(self):
        return self.team.world

    @property
    def goal(self):
        return self.team.goal

    @property
    def goalie(self):
        return self.team.goalie

    @property
    def ball(self):
        return self.world.ball

    def check_new_robots(self):
        # dynamically create a set of tactics for new robots
        for robot in self.team:
            r_id = robot.uid
            if r_id not in self.players:
                self.players[r_id] = {}
                for key, expression in self.tactics_factory.iteritems():
                    self.players[r_id][key] = expression(robot)

    def setup_tactics(self):
        """
        When overloading this method, remember to set each robot's current_tactic to a
        steppable. If a robot doesn't have a current_tactic at the end of the step, shit
        WILL happen. You have been warned.
        """
        raise NotImplementedError

    def execute_step(self):
        for robot in self.team:
            robot.current_tactic.step()

    def _step(self):
        self.check_new_robots()
        self.setup_tactics()
        self.execute_step()

    def step(self):
        self._step()
        self.team.play = self
