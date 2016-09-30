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
import logging

from .. import Play
from ..tactics.goalkeeper import Goalkeeper
from ..tactics.zickler43 import Zickler43
from ..tactics.blocker import Blocker
from ..tactics.defender import Defender


logger = logging.getLogger(__name__)


class AutoRetaliate(Play):
    """
    A goalkeeper, and attacker (Zickler43), a blocker, and the
    rest are defenders. The goalkeeper must be set, the attacker
    is the closest to the ball, the blocker the second closer,
    and the rest are defenders matched against some enemies.

    This is basically it.
    """

    def __init__(self, team, **kwargs):
        """
        team: duh
        """
        super(AutoRetaliate, self).__init__(team, **kwargs)
        self.players = {}
        self.tactics_factory.update({
            'goalkeeper': lambda robot: Goalkeeper(robot, aggressive=True, angle=0.),
            'attacker': lambda robot: Zickler43(robot, always_force=True, always_chip=False, respect_mid_line=True),
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

        atk_id = closest_robots[0] if len(closest_robots) > 0 else None
        blk_id = closest_robots[1] if len(closest_robots) > 1 else None

        # gather the defenders (not goalkeeper, attacker or blocker)
        defenders = [r for r in self.team if r.uid not in [gk_id, atk_id, blk_id]]
        # order defenders by id to avoid position oscillations
        defenders = sorted(defenders, key=lambda r: r.uid)
        # distributing defenders
        # TODO: make it generic
        defender_arc = {}
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
                if (defender_arc and r_id in defender_arc):
                    robot.current_tactic.arc = defender_arc[r_id]
