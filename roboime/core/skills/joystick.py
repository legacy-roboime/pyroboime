import pygame
pygame.init()

from .. import Skill
from ..skills.fishingrod import FishingRod


class Joystick(Skill):
    """
    This tactic enables joystick control for a robot.
    It uses the library 'pygame'.
    """

    speed_ratio = 2.0
    angle_ratio = 180.0

    def __init__(self, robot, **kwargs):
        super(Joystick, self).__init__(robot, deterministic=True, **kwargs)
        if pygame.joystick.get_count() == 0:
            self.joystick_found = False
            # raise RuntimeError('No joysticks found.')
            print 'WARNING: No joysticks found.'
        else:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.fishingrod = FishingRod(robot, b_angle=0)

            self.chipkick_button = 3
            self.kick_button = 0
            self.dribble_button = 2
            self.straffe_button = 1

            self.normal_axis = 1
            self.aux_axis = 0
            self.power_axis = 2

    def _step(self):
        if self.joystick_found:
            # User did something
            for event in pygame.event.get():
                pass
                ## Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
                #if event.type == pygame.JOYBUTTONDOWN:
                #    print("Joystick button pressed.")
                #if event.type == pygame.JOYBUTTONUP:
                #    print("Joystick button released.")
            x = self.joystick.get_axis(self.aux_axis)
            y = -self.joystick.get_axis(self.normal_axis)
            power = (1 - self.joystick.get_axis(self.power_axis)) / 2

            if self.joystick.get_button(self.kick_button):
                self.robot.action.kick = power
            elif self.joystick.get_button(self.chipkick_button):
                self.robot.action.chipkick = power
            elif self.joystick.get_button(self.dribble_button):
                self.robot.action.dribble = power

            if self.joystick.get_button(self.straffe_button):
                self.robot.action.speeds = y * self.speed_ratio, -x * self.speed_ratio, 0.0
            else:
                self.robot.action.speeds = y * self.speed_ratio, 0.0, -x * self.angle_ratio
