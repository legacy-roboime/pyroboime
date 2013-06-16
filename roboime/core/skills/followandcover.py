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
