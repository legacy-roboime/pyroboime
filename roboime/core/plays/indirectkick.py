from numpy import linspace
from time import time
from ...utils.geom import Point
from ...utils.geom import Line

from .. import Play
from ..tactics.goalkeeper import Goalkeeper
from ..tactics.blocker import Blocker
from ..tactics.defender import Defender
from ..skills.goto import Goto


class IndirectKick(Play):
    """
    Currently this play will extend StopReferee by performing an
    indirect kick by positioning a robot on a good spot and making
    a pass to it.
    """

    def __init__(self, team, goalkeeper_uid, **kwargs):
        super(IndirectKick, self).__init__(team, **kwargs)
        self.goalkeeper_uid = goalkeeper_uid
        self.players = {}
        self.team = team
        self.tactics_factory = lambda robot: {
            'goalkeeper': Goalkeeper(robot, aggressive=False, angle=0),
            'blocker': Blocker(robot, arc=0),
            'receiver': Goto(robot),
        }

    def get_best_indirect_positions(self, target=None, precision=6):
        """
        Discretizes points over the field (respecting a minimum border from the field,
        and without entering none of the defense areas), according to given precision.
        Searches for clear paths between initial position (ball), intermediate position,
        and the target.
        
        Returns a sorted list of tuples (Points that are closer to the target come 
        first):
        [(point, distance_to_target), (point, distance_to_target), (point, distance_to_target), ...]
        """
        # TODO: aim for the best spot in the goal, not only to the middle of the enemy goal

        t = self.team
        b = self.ball

        if target is None:
            target = self.team.enemy_goal

        candidate = []

        safety_margin = 2 * self.team[0].radius + 0.1

        # field params:
        f_l = self.world.length - self.world.defense_radius - safety_margin
        f_w = self.world.width - safety_margin

        # candidate points in the field range
        for x in linspace(-f_l/2, f_l/2, precision):
            for y in linspace(-f_w/2, f_w/2, precision - 2):
                pt = Point(x, y)
                acceptable = True
                for enemy in self.world.enemy_team(t.color).iterrobots():
                    # if the robot -> pt line doesn't cross any enemy body...
                    if not Line(b, pt).crosses(enemy.body):
                        final_line = Line(pt, target)
                        # if the pt -> target line crosses any enemy body...
                        if final_line.crosses(enemy.body):
                            acceptable = False
                if acceptable:
                    candidate += [(pt, final_line.length)]
        if not candidate:
            return [(Point(0,0))]
        else:
            return sorted(candidate, key=lambda tup: tup[1])

    def step(self):
        # dynamically create a set of tactics for new robots
        for robot in self.team:
            r_id = robot.uid
            if r_id not in self.players:
                self.players[r_id] = self.tactics_factory(robot)

        all_robots = [r.uid for r in self.team.iterrobots()]

        # make sure we do not account for the goalkeeper on that list
        gk_id = self.goalkeeper_uid
        if gk_id in all_robots:
            all_robots.remove(gk_id)

        atk_id = all_robots[0] if len(all_robots) > 0 else None

        for robot in self.team:
            r_id = robot.uid
            if r_id == gk_id:
                self.players[r_id]['goalkeeper'].step()
            elif r_id == atk_id:
                self.players[r_id]['receiver'].target = self.get_best_indirect_positions()[0][0]
                self.players[r_id]['receiver'].step()
            else:
                self.players[r_id]['blocker'].step()