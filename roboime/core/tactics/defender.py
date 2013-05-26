from .. import Tactic
from ...utils.statemachine import Transition
from ..skills.drivetoobject import DriveToObject
from ..skills.followandcover import FollowAndCover

class Defender(Tactic):
    """
    If you need robots on the defense line, use this.

    Also one may want a closer body-to-body defense, in that
    case you may set an enemy.

    Remember that you may not only defend the goal, you're allowed
    to defend any point on the field.
    """
    def __init__(self, robot, enemy, cover=None, dist=0.5, fac_dist=0.3, min_dist=3.):
        self.min_dist = min_dist
        self.cover = robot.goal if cover is None else cover
        self.follow_and_cover = FollowAndCover(robot, follow=enemy, cover=self.cover, distance=fac_dist)
        self.drive_to_object = DriveToObject(
            robot,
            point=self.cover,
            lookpoint=enemy,
            threshold=-(dist + robot.front_cut),
            max_error_d=0.1, # TODO parametrize
            max_error_a=10, # TODO parametrize
        )
        super(Defender, self).__init__(
            [robot],
            deterministic=True, 
            states=[self.follow_and_cover, self.drive_to_object],
            initial_state=self.drive_to_object,
        )
        self.transitions = [
            Transition(self.drive_to_object, self.follow_and_cover, condition=lambda: enemy.distance(robot.goal) < self.min_dist),
            Transition(self.follow_and_cover, self.drive_to_object, condition=lambda: enemy.distance(robot.goal) > self.min_dist),
        ]
