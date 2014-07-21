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
from .. import Play
from ..tactics.goalkeeper import Goalkeeper
from ..tactics.blocker import Blocker
from ..tactics.defender import Defender


class Stop(Play):
    """
    Whenever you need to position the robots without getting too close
    to the ball, use this.
    """

    def __init__(self, team, **kwargs):
        super(Stop, self).__init__(team, **kwargs)
        self.players = {}
        self.tactics_factory.update({
            'goalkeeper': lambda robot: Goalkeeper(robot, aggressive=False, angle=0),
            'blocker': lambda robot: Blocker(robot, arc=0),
            'defender': lambda robot: Defender(robot, enemy=self.ball),
        })

    def setup_tactics(self):
        # list of the ids of the robots in order of proximity to the ball
        closest_robots = [r.uid for r in self.team.closest_robots_to_ball(can_kick=True)]

        # make sure we do not account for the goalkeeper on that list
        gk_id = self.goalie
        if gk_id in closest_robots:
            closest_robots.remove(gk_id)

        # first 3 are blockers, the rest are defenders
        blockers, defenders = closest_robots[:3], closest_robots[3:]
        #blockers = [r for d, r in sorted((-self.team[id].y, id) for id in blockers)]
        #print blockers

        # sorting to avoid robot swap
        blockers = sorted(blockers)

        # order defenders by id to avoid position oscillations
        defenders = sorted(defenders)

        # grab the actual list of defenders
        defenders = [self.team[i] for i in defenders]

        # distributing defenders
        if len(defenders) == 3:
            defender_arc = {
                defenders[0].uid: -15.0,
                defenders[1].uid: 0.0,
                defenders[2].uid: 15.0
            }
        elif len(defenders) == 2:
            defender_arc = {
                defenders[0].uid: -10,
                defenders[1].uid: 10
            }
        elif len(defenders) == 1:
            defender_arc = {
                defenders[0].uid: 0.0
            }


        # iterate over list of enemies by proximity to the goal
        #for enemy in self.enemy_team.closest_robots_to_point(self.team.goal):
        #    # if there are free defenders, assign the closest to the enemy, to follow it
        #    if len(defenders) > 0:
        #        defender = enemy.closest_to(defenders)
        #        defenders.remove(defender)
        #        self.players[defender.uid]['defender'].enemy = enemy
        ## for any remaining defender, let them guard the ball
        for defender in defenders:
            self.players[defender.uid]['defender'].enemy = self.ball

        # set blockers arc
        if len(blockers) > 0:
            self.players[blockers[0]]['blocker'].arc = 0
        if len(blockers) > 1:
            self.players[blockers[1]]['blocker'].arc = 30
        if len(blockers) > 2:
            self.players[blockers[2]]['blocker'].arc = -30

        for robot in self.team:
            r_id = robot.uid
            if r_id == gk_id:
                robot.current_tactic = self.players[r_id]['goalkeeper']
            elif r_id in blockers:
                robot.current_tactic = self.players[r_id]['blocker']
            else:
                robot.current_tactic = self.players[r_id]['defender']
                robot.current_tactic.arc = defender_arc[r_id]
