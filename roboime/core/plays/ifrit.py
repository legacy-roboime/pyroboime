
from .. import Play
from ..tactics.goalkeeper import Goalkeeper
from ..tactics.zickler43 import Zickler43
from ..tactics.blocker import Blocker
from ..tactics.defender import Defender
from ..tactics.executepass import ExecutePass
from ..tactics.receivepass import ReceivePass

class Ifrit(Play):
    """
    This is the first cooperative play in this project.

    Basically, set the closest robot to the ball to be either an attacker
    - in case he has a clear shot to the goal - or a passer, if he does not.

    We'll have a second robot in a receiving position: a pivot, which will
    be ready to receive the ball. 

    The rest is the same as the autoretaliate play.
    """
    backoff_probability = 0.75

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


        # Here we split from autoretaliate.         
        # We'll find now the best position for our pivot to receive a possible pass.
        best_position = self.team.best_indirect_positions()[0][0]
        robots_closest_to_bathtub = self.team.closest_robots_to_point(point=best_position)
        robots_closest_to_bathtub.remove(self.team[atk_id])
        robots_closest_to_bathtub.remove(self.team[gk_id])
        
        # Here, we'll get a pivot.
        pvt_id = robots_closest_to_bathtub[0].uid if len(robots_closest_to_bathtub) > 0 else None
        
        closest_robots.remove(pvt_id)
        
        blk_id = closest_robots[1] if len(closest_robots) > 1 else None

        # gather the defenders (not goalkeeper, attacker, pivot or blocker)
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

        # Setting position for the pivot 
        self.players[pvt_id]['receiver'].point = best_position
        
        # Check if we want to pass or if we want to kick.
        if self.world.has_clear_shot(self.players[atk_id]['attacker'].lookpoint):
            goal_kick = True
            self.players[pvt_id]['receiver'].companion = self.players[atk_id]['attacker']
            print self.players[pvt_id]['receiver'].companion, self.players[atk_id]['attacker']
        else:
            self.players[atk_id]['passer'].companion = self.players[pvt_id]['receiver']
            self.players[pvt_id]['receiver'].companion = self.players[atk_id]['passer']
            goal_kick = False

        # step'em, this is needed to guarantee we're only stepping active robots
        for robot in self.team:
            r_id = robot.uid
            if r_id == gk_id:
                robot.current_tactic = self.players[r_id]['goalkeeper']
            elif r_id == atk_id and goal_kick:
                robot.current_tactic = self.players[r_id]['attacker']
            elif r_id == atk_id and not goal_kick:
                robot.current_tactic = self.players[r_id]['passer']
            elif r_id == blk_id:
                robot.current_tactic = self.players[r_id]['blocker']
            elif r_id == pvt_id:
                robot.current_tactic = self.players[r_id]['receiver']
            else:
                robot.current_tactic = self.players[r_id]['defender']
