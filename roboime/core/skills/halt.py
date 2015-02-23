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
from .. import Skill


class Halt(Skill):
    """
    This skill will stop the robot by setting its action target
    to its current position.
    """

    def __init__(self, robot, deterministic=True, **kwargs):
        super(Halt, self).__init__(robot, deterministic=deterministic, **kwargs)

    def _step(self):
        self.robot.action.absolute_speeds = (0, 0, 0)
        self.robot.skill = self
