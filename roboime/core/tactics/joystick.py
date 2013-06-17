from numpy.linalg import norm
from numpy import array
import pygame
pygame.init()

from .. import Tactic
from ..skills.fishingrod import FishingRod
from ...utils.geom import Point
from ...utils.mathutils import atan2


class Joystick(Tactic):
    """
    This tactic enables joystick control for a robot.
    It uses the library 'pygame'.
    """

    speed_ratio = 2.0
    angle_ratio = 180.0

    def __init__(self, robot, **kwargs):
        super(Joystick, self).__init__(robot, deterministic=True, **kwargs)
        if pygame.joystick.get_count() == 0:
            # raise RuntimeError('No joysticks found.')
            print 'WARNING: No joysticks found.'
        else:    
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.fishingrod = FishingRod(robot, b_angle = 0)

            self.chipkick_button = 3
            self.kick_button = 0
            self.dribble_button = 2
            self.straffe_button = 1

            self.normal_axis = 1
            self.aux_axis = 0
            self.power_axis = 2
        

    def _step(self):
        # EVENT PROCESSING STEP
        for event in pygame.event.get(): # User did something
            pass
            ## Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
            #if event.type == pygame.JOYBUTTONDOWN:
            #    print("Joystick button pressed.")
            #if event.type == pygame.JOYBUTTONUP:
            #    print("Joystick button released.")
        if pygame.joystick.get_count() == 0:
            print 'WARNING: No joysticks found.'
            self.robot.action.speeds = 0.0, 0.0, 90 * self.speed_ratio
        else:
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
        
            #angle = atan2(y, x)
            #rod = array((x, y))

            #self.fishingrod.threshold = norm(rod) * self.speed_ratio
            #self.fishingrod.b_angle = angle
            #self.fishingrod.t_angle = angle
            #self.fishingrod.angle = angle
            #self.fishingrod.step()
