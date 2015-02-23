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
from numpy import array
from numpy.linalg import norm

from .goto import Goto
from ...utils.geom import Point


class FollowAndCover(Goto):
    """
    When you need to follow a point but cover another
    while maintaining a constant distance from the
    followed, this is the way to go.
    """

    def __init__(self, robot, follow, cover, distance=1.0, **kwargs):
        """
        The argument names are pretty self explanatory,
        If not, here's a drawing:

            X <------- cover
             \
              \
              (O) <--- robot
                \ <--- distance
                 X <-- follow

        Notice that the points follow, robot, and cover are
        aligned. And that follow and robot are `distance` apart.
        """
        super(FollowAndCover, self).__init__(robot, **kwargs)
        self.follow = follow
        self.cover = cover
        self.distance = distance

    def _step(self):
        # vector from follow to cover:
        f2c = array(self.cover) - array(self.follow)
        # normalized:
        vec = f2c / norm(f2c)
        # target is follow displaced of distance over vec
        self.target = Point(array(self.follow) + vec * self.distance)

        # let Goto do its thing
        super(FollowAndCover, self)._step()
