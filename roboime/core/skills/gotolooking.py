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
from .goto import Goto


class GotoLooking(Goto):
    def __init__(self, robot, lookpoint=None, **kwargs):
        """
        lookpoint: Where you want it to look, what were you expecting?
        """
        super(GotoLooking, self).__init__(robot, **kwargs)
        self._lookpoint = lookpoint

    @property
    def lookpoint(self):
        if callable(self._lookpoint):
            return self._lookpoint()
        else:
            return self._lookpoint

    @lookpoint.setter
    def lookpoint(self, value):
        self._lookpoint = value

    def _step(self):
        #print self.lookpoint
        self.angle = self.robot.angle_to_point(self.lookpoint)
        super(GotoLooking, self)._step()
