from .. import Play
from ..tactics.goalkeeper import Goalkeeper
from ..tactics.blocker import Blocker
from ..tactics.defender import Defender


class Stop(Play):
    """
    Whenever you need to position the robots without getting too close
    to the ball, use this.
    """

    def __init__(self, team, goalkeeper_uid, **kwargs):
        super(Stop, self).__init__(team, **kwargs)
        self.goalkeeper_uid = goalkeeper_uid
        self.players = {}
        self.tactics_factory.update({
            'goalkeeper': lambda robot: Goalkeeper(robot, aggressive=False, angle=0),
            'blocker': lambda robot: Blocker(robot, arc=0),
            'defender': lambda robot: Defender(robot, enemy=self.ball, distance=0.6),
        })

    def setup_tactics(self):
        # list of the ids of the robots in order of proximity to the ball
        closest_robots = [r.uid for r in self.team.closest_robots_to_ball(can_kick=True)]

        # make sure we do not account for the goalkeeper on that list
        gk_id = self.goalkeeper_uid
        if gk_id in closest_robots:
            closest_robots.remove(gk_id)

        # first 3 are blockers, the rest are defenders
        blockers, defenders = closest_robots[:3], closest_robots[3:]

        # grab the actual list of defenders
        defenders = [self.team[i] for i in defenders]

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

        # set blockers arc
        if len(blockers) > 0:
            self.players[blockers[0]]['blocker'].arc = 0
        if len(blockers) > 1:
            self.players[blockers[1]]['blocker'].arc = 23
        if len(blockers) > 2:
            self.players[blockers[2]]['blocker'].arc = -23

        for robot in self.team:
            r_id = robot.uid
            if r_id == gk_id:
                robot.current_tactic = self.players[r_id]['goalkeeper']
            elif r_id in blockers:
                robot.current_tactic = self.players[r_id]['blocker']
            else:
                robot.current_tactic = self.players[r_id]['defender']
