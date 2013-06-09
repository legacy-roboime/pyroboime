"""
This is the core module that holds the base for Skills,
Tactics and Plays.
Might it be splitted?
"""
from ..utils.statemachine import State, Machine


class Skill(State):

    def __init__(self, robot, deterministic):
        super(Skill, self).__init__(deterministic)
        self.robot = robot

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

    def step(self):
        pass


class Tactic(Machine):

    def __init__(self, robots, deterministic, **kwargs):
        super(Tactic, self).__init__(deterministic, **kwargs)
        self.robots = robots

    @property
    def robot(self):
        return self.robots[0]

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

    def step(self):
        if self.current_state is not None:
            self.current_state.step()
        self.execute()


class Play(object):

    def __init__(self, team):
        '''
        When constructing a derived play, keep in mind tactics_factory is a dictionary
        of lambda expressions that generate a steppable for a given robot. 
        
        DO NOT overwrite the tactics_factory of your base play under any circumstances,
        under penalty of breaking the base play. Use tactics_factory.update(new_factory)
        instead. Remember to not use any keys already in your base factory.
        '''

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
        '''
        When overloading this method, remember to set each robot's current_tactic to a
        steppable. If a robot doesn't have a current_tactic at the end of the step, shit
        WILL happen. You have been warned.
        '''
        raise NotImplementedError
   
    def execute_step(self):
        for robot in self.team:
            robot.current_tactic.step()

    def step(self):
        self.check_new_robots()
        self.setup_tactics()
        self.execute_step()
