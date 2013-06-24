
from .. import Play
from ..tactics.goalkeeper import Goalkeeper
from ..tactics.zickler43 import Zickler43
from ..tactics.blocker import Blocker
from ..tactics.defender import Defender
from ..tactics.executepass import ExecutePass
from ..tactics.receivepass import ReceivePass
from ..tactics.

class Ifrit(Play):
    """
    Basically, set the closest robot to the ball to be either an attacker
    - in case he has a clear shot to the goal - or a passer, if he does not.

    We'll have a second robot in an attacking position: a pivot, which will
    be ready to receive the ball. 

    The rest is the same as the autoretaliate play.
    """
    self.backoff_probability = 0.75

    def __init__(self, team, **kwargs):
        """
        team: duh
        """
        super(Ifrit, self).__init__(team, **kwargs)
        self.pass_probability = self.backoff_probability
        self.players = {}
        self.tactics_factory.update({
            'goalkeeper': lambda robot: Goalkeeper(robot, aggressive=False, angle=0),
            'attacker': lambda robot: Zickler43(robot),
            'blocker': lambda robot: Blocker(robot, arc=0),
            'defender': lambda robot: Defender(robot, enemy=self.ball, distance=0.6),
            'passer': lambda robot: ExecutePass(robot),
            'receiver': lambda robot: ReceivePass(robot),
        })

    def setup_tactics(self):
        # list of the ids of the robots in order of proximity to the ball
        closest_robots = [r.uid for r in self.team.closest_robots_to_ball(can_kick=True)]

        # make sure we do not account for the goalkeeper on that list
        gk_id = self.goalie
        if gk_id in closest_robots:
            closest_robots.remove(gk_id)

        atk_id = closest_robots[0] if len(closest_robots) > 0 else None
        # Here, we'll get a pivot.
        pvt_id = closest_robots[1] if len(closest_robots) > 1 else None
        blk_id = closest_robots[2] if len(closest_robots) > 2 else None

        # gather the defenders (not goalkeeper, atacker or blocker)
        defenders = [r for r in self.team if r.uid not in [gk_id, atk_id, blk_id, pvt_id]]

        # iterate over list of enemies by proximity to the goal
        for enemy in self.enemy_team.closest_robots_to_point(self.team.goal):
            # if there are free defenders, assign the closest to the enemy, to follow it
            if len(defenders) > 0:
                defender = enemy.closest_to(defenders)
                defenders.remove(defender)
                self.players[defender.uid]['defender'].enemy = enemy

        # for any remaining defender, let them guard the ball
        for defender in defenders:
            self.players[defender.uid]['defender'].enemy = self.ball

        # Here we split from autoretaliate.         
        # We'll find now the best position for our pivot to receive a possible pass.
        self.best_position = self.team.best_indirect_positions()[0][0]

        point_to_kick = self.players[atk_id]['attacker'].lookpoint
        
        #Check if we want to pass or if we want to kick.

        # step'em, this is needed to guarantee we're only stepping active robots
        for robot in self.team:
            r_id = robot.uid
            if r_id == gk_id:
                robot.current_tactic = self.players[r_id]['goalkeeper']
            elif r_id == atk_id:
                robot.current_tactic = self.players[r_id]['attacker']
            elif r_id == blk_id:
                robot.current_tactic = self.players[r_id]['blocker']
            else:
                robot.current_tactic = self.players[r_id]['defender']
