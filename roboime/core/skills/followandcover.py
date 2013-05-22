from .goto import Goto


class FollowAndCover(Goto):
    """
    When you need to follow a point but cover another
    while maintaining a constant distance from the
    followed, this is the way to go.
    """

    def __init__(self, robot, follow, cover, distance):
        """
        The argument names are pretty self explainable,
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
        pass
    # TODO
