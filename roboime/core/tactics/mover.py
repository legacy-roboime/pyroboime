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
from .. import Tactic
#from ...utils.statemachine import Transition
from ..skills.gotolooking import GotoLooking


class Mover(Tactic):
    """
    Goto A then look to B then goto B then look to A then repeat, that's it.
    """

    def __init__(self, robot, target):
        self.target = target
        self.goto = GotoLooking(
            robot,
            name='Goto',
            target=lambda: self.target,
            lookpoint=robot.world.ball
        )

        super(Mover, self).__init__(robot, initial_state=self.goto)
