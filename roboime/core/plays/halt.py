from .. import Play
from ..skills.halt import Halt as HaltSkill


class Halt(Play):
    """Alright, stop! And don't move."""

    def __init__(self, team, **kwargs):
        super(Halt, self).__init__(team, **kwargs)
        self.players = {}

    def step(self):
        # dynamically create a set of tactics for new robots
        for robot in self.team:
            r_id = robot.uid
            if r_id not in self.players:
                self.players[r_id] = HaltSkill(robot)
            self.players[r_id].step()
