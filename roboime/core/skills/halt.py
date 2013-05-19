from .. import Skill


class Halt(Skill):
    """
    This skill will stop the robot by setting its action target
    to its current position.
    """

    def step(self):
        self.robot.action.absolute_speeds = 0, 0, 0
