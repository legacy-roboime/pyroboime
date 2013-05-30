from .. import Skill


class Halt(Skill):
    """
    This skill will stop the robot by setting its action target
    to its current position.
    """

    def __init__(self, robot, deterministic=True, **kwargs):
        super(Halt, self).__init__(robot, deterministic=deterministic, **kwargs)

    def step(self):
        self.robot.action.absolute_speeds = (0, 0, 0)
        self.robot.skill = self
