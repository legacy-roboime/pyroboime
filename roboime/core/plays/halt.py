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
