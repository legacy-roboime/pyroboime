from .. import Play
from ..tactics.goalkeeper import Goalkeeper
from ..tactics.zickler43 import Zickler43
from ..tactics.blocker import Blocker
from ..tactics.defender import Defender


class AutoRetaliate(Play):
    """
    A goalkeeper, and attacker (Zickler43), a blocker, and the
    rest are defenders. The goalkeeper must be set, the attacker
    is the closest to the ball, the blocker the second closer,
    and the rest are defenders matched against some enemies.

    This is basically it.
    """

    def __init__(self, team, goalkeeper_uid, **kwargs):
        """
        team: duh
        goalkeeper_uid: uid of the robot that should be the goalkeeper
        """
        super(AutoRetaliate, self).__init__(team, **kwargs)
        self.goalkeeper_uid = goalkeeper_uid
        self.players = {}
        self.tactics_factory = lambda robot: {
            'goalkeeper': Goalkeeper(robot, aggressive=False, angle=0),
            'attacker': Zickler43(robot),
            'blocker': Blocker(robot, arc=0),
            'defender': Defender(robot, enemy=self.ball, distance=0.6),
        }

    def step(self):
        # dynamically create a set of tactics for new robots
        for robot in self.team:
            r_id = robot.uid
            if r_id not in self.players:
                self.players[r_id] = self.tactics_factory(robot)

        # list of the ids of the robots in order of proximity to the ball
        closest_robots = [r.uid for r in self.team.closest_robots_to_ball(can_kick=True)]

        # make sure we do not account for the goalkeeper on that list
        gk_id = self.goalkeeper_uid
        if gk_id in closest_robots:
            closest_robots.remove(gk_id)

        atk_id = closest_robots[0] if len(closest_robots) > 0 else None
        blk_id = closest_robots[1] if len(closest_robots) > 1 else None

        # gather the defenders (not goalkeeper, atacker or blocker)
        defenders = [r for r in self.team if r.uid not in [gk_id, atk_id, blk_id]]

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

        # step'em, this is needed to guarantee we're only stepping active robots
        for robot in self.team:
            r_id = robot.uid
            if r_id == gk_id:
                self.players[r_id]['goalkeeper'].step()
            elif r_id == atk_id:
                self.players[r_id]['attacker'].step()
            elif r_id == blk_id:
                self.players[r_id]['blocker'].step()
            else:
                self.players[r_id]['defender'].step()
