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
    def __init__(self, robot, enemy, cover=None, distance=0.5, follow_distance=0.3, proximity=3.0, flapping_margin=0.1):
        """
        cover: point or object to cover
        distance: distance to keep from the cover point
        follow_distance: distance to keep from the enemy when following it
        proximity: distance to switch from covering mode to following mode
        flapping_margin: distance margin to avoid flapping between covering and following
        """
        self.proximity = proximity
        self.cover = robot.goal if cover is None else cover
        self.distance = distance
        self.follow_distance = follow_distance
        self.proximity = proximity
        self.flapping_margin = flapping_margin
        self._enemy = enemy
        self.follow_and_cover = FollowAndCover(
            robot,
            follow=self.enemy,
            cover=self.cover,
            distance=self.follow_distance,
            referential=self.enemy,
        )
        self.drive_to_object = DriveToObject(
            robot,
            point=self.cover,
            lookpoint=self.enemy,
            threshold=-(self.distance + robot.radius),
        )
        # the following line is so that lambdas can use self.robot instead of robot and keep track of the robot
        # even if it changes, although tactics are supposed to never change its robot we're trying to keep it
        # flexible
        self._robot = robot
        super(Defender, self).__init__(
            robot,
            deterministic=True,
            initial_state=self.drive_to_object,
            transitions=[
                Transition(self.drive_to_object, self.follow_and_cover, condition=lambda: self.enemy.distance(self.robot.goal) < self.proximity - self.flapping_margin),
                Transition(self.follow_and_cover, self.drive_to_object, condition=lambda: self.enemy.distance(self.robot.goal) > self.proximity + self.flapping_margin),
            ]
        )

    @property
    def enemy(self):
        return self._enemy

    @enemy.setter
    def enemy(self, new_enemy):
        self._enemy = new_enemy
        self.follow_and_cover.follow = new_enemy
        self.follow_and_cover.referential = new_enemy
        self.drive_to_object.lookpoint = new_enemy
