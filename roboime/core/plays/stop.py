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
from itertools import permutations

from .. import Play
from ..tactics.goalkeeper import Goalkeeper
from ..tactics.blocker import Blocker
from ..tactics.defender import Defender


class Stop(Play):
    """
    Whenever you need to position the robots without getting too close
    to the ball, use this.
    """

    # map the number of robots to a list of arc angles
    defender_arcs = {
        0: {},
        1: {0},
        2: {-10, 10},
        3: {-15, 0, 15},
        4: {-21, -7, 7, 21},
        5: {-24, -12, 0, 12, 24},
    }
    blocker_arcs = {
        0: {},
        1: {0},
        2: {-15, 15},
        3: {-30, 0, 30},
        4: {-45, -15, 15, 45},
        5: {-60, -30, 0, 30, 60},
    }

    default_n_blockers = 2

    def __init__(self, team, **kwargs):
        super(Stop, self).__init__(team, **kwargs)
        self.players = {}
        self.tactics_factory.update({
            'goalkeeper': lambda robot: Goalkeeper(robot, aggressive=False, angle=0),
            'blocker': lambda robot: Blocker(robot, arc=0),
            'defender': lambda robot: Defender(robot, enemy=self.ball),
        })
        self.n_blockers = self.default_n_blockers
        self.cached_gk_id = None
        self.cached_bd_ids = None
        self.counter = 0

    def heavy_setup_tactics(self):
        gk_id = self.cached_gk_id
        bd_ids = self.cached_bd_ids

        # first 3 are blockers, the rest are defenders
        n_blockers = min(self.n_blockers, len(bd_ids))
        n_defenders = len(bd_ids) - n_blockers

        # get arcs
        defender_arcs = self.defender_arcs[n_defenders]
        blocker_arcs = self.blocker_arcs[n_blockers]

        # create jobs
        jobs = {('defender', a) for a in defender_arcs} | {('blocker', a) for a in blocker_arcs}

        # distribute the jobs
        best_job_map = None
        best_job_dist = None
        for job_set in permutations(jobs):
            job_map = [(i, j[0], j[1]) for i, j in zip(bd_ids, job_set)]
            job_dist = sum(self.players[i][j].dist_to_arc(a) for i, j, a in job_map)
            if best_job_dist is None or job_dist < best_job_dist:
                best_job_dist = job_dist
                best_job_map = job_map

        # assign tactics
        if gk_id is not None:
            self.team[gk_id].current_tactic = self.players[gk_id]['goalkeeper']
        for i, j, a in best_job_map:
            tactic = self.players[i][j]
            tactic.arc = a
            self.team[i].current_tactic = tactic

    def setup_tactics(self):
        gk_id = self.goalie
        # blockers and defenders
        bd_ids = {r.uid for r in self.team if r.uid != gk_id}

        # this is a strategy to only call heavy_setup_tactics only once every 300 frames or one the requirements change
        if self.counter > 300 or gk_id != self.cached_gk_id or bd_ids != self.cached_bd_ids:
            self.cached_gk_id = gk_id
            self.cached_bd_ids = bd_ids
            self.heavy_setup_tactics()
            self.counter = 0
        else:
            self.counter += 1
