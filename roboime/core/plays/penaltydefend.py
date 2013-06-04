from numpy import array

from .. import Play
from ..tactics import Goalkeeper
from ..skills import Goto
from ...utils.geom import Point


class PenaltyDefend(Play):
    """
    Pretty straight forward too, defend a penalty.
    """
    def __init__(self, team, goalkeeper_uid, **kwargs):
        super(PenaltyDefend, self).__init__(team, **kwargs)
        self.goalkeeper_uid = goalkeeper_uid
        self.players = {}
        self.tactics_factory = lambda robot: {
            'goalkeeper': Goalkeeper(robot, aggressive=False, angle=0),
            'goto': Goto(robot),
        }

    def step(self):
        gk_id = self.goalkeeper_uid

        # dynamically create a set of tactics for new robots
        for robot in self.team:
            r_id = robot.uid
            if r_id not in self.players:
                self.players[r_id] = self.tactics_factory(robot)

        for robot in self.team:
            r_id = robot.uid
            if r_id == gk_id:
                self.players[r_id]['goalkeeper'].step()
            else:
                self.players[r_id]['goto'].target = Point(array(self.goal.penalty_line)[0] - array(robot.radius, robot.radius * 3 * r_id))
                self.players[r_id]['goto'].step()
