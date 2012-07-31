"""
This is the skill package.

Put new skill in this package, please inherit your skills from Skill.
"""

class Skill(object):
    """
    This is the base Skill, currently it only holds a robot, this is intended
    to be used from the robot, and not directly from the skill, although that
    should be possible.
    """

    def __init__(self):
        """
        Note that it's either possible to assign a robot to a skill or a skill to
        a robot, by acessing robot.skill or skill.robot both will update each other.
        """
        self._robot = None

    @property
    def robot(self):
        return self._robot

    @robot.setter
    def robot(self, nrobot):
        nrobot._skill = self
        self._robot = nrobot

    def step(self):
        #TODO: raise proper exception
        raise Exception("Skill not implemented.")

