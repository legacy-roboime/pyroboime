from numpy import array
from numpy import sign

from .. import Play
from ..tactics.goalkeeper import Goalkeeper
from ..tactics.zickler43 import Zickler43
from ..skills.goto import Goto
from ...utils.geom import Point


class Penalty(Play):
    """
    Pretty straightforward, go there and kick a penalty.
    """
    # FIXME: final goto might be crashing grSim ODE:
    # description:
    # error0: "assertion 'bNormalizationResult' failed in ..\..\include\ode/odemath.h"
    # error1: "assertion 'context->isStructureValid()' failed in ..\..\ode\src\util.cpp:665"

    def __init__(self, team, goalkeeper_uid, **kwargs):
        super(Penalty, self).__init__(team, **kwargs)
        self.goalkeeper_uid = goalkeeper_uid
        self.players = {}
        self.tactics_factory = lambda robot: {
            'goalkeeper': Goalkeeper(robot, aggressive=False, angle=0),
            'attacker': Zickler43(robot),
            'goto': Goto(robot),
        }

    def step(self):
        # list of the ids of the robots in order of proximity to the ball
        closest_robots = [r.uid for r in self.team.closest_robots_to_ball(can_kick=True)]

        # make sure we do not account for the goalkeeper on that list
        gk_id = self.goalkeeper_uid
        if gk_id in closest_robots:
            closest_robots.remove(gk_id)

        atk_id = closest_robots[0] if len(closest_robots) > 0 else None

        # dynamically create a set of tactics for new robots
        for robot in self.team:
            r_id = robot.uid
            if r_id not in self.players:
                self.players[r_id] = self.tactics_factory(robot)

        for robot in self.team:
            r_id = robot.uid
            if r_id == gk_id:
                self.players[r_id]['goalkeeper'].step()
            elif r_id == atk_id:
                self.players[r_id]['attacker'].step()
            else:
                self.players[r_id]['goto'].target =  Point(array(self.goal.penalty_line)[0] * (-1) - array((robot.radius * -1 * sign(self.goal.x), robot.radius * 3 * (1 + r_id))))
                self.players[r_id]['goto'].step()