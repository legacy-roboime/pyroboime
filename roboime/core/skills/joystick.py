import pygame
from numpy import abs

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
        pygame.init()
        pygame.joystick.init()
        self.check_joysticks()
        # if pygame.joystick.get_count() == 0:
            # self.joystick_found = False
            # # raise RuntimeError('No joysticks found.')
            # print 'WARNING: No joysticks found.'
            # pygame.joystick.quit()
            # pygame.quit()
        # else:
            # self.joystick_found = True
            # self.joystick = pygame.joystick.Joystick(0)
            # self.joystick.init()
            # self.fishingrod = FishingRod(robot, b_angle=0)

            # self.chipkick_button = 3
            # self.kick_button = 0
            # self.dribble_button = 2
            # self.straffe_button = 1

            # self.normal_axis = 1
            # self.aux_axis = 0
            # self.power_axis = 2

            
            #nr eixos, nr hats, nr botoes
    
        

    def check_joysticks(self, index=0):
        if pygame.joystick.get_count() == 0:
            self.joystick_found = False
            # raise RuntimeError('No joysticks found.')
            print 'WARNING: No joysticks found.'
            pygame.joystick.quit()
            pygame.quit()
        else:
            if index < pygame.joystick.get_count():
                # Available joysticks: ADD NEW JOYSTICK TEMPLATES HERE!
                # name_of_joystick = (numaxes, numhats, numbuttons)
                available_templates = {
                    'xbox': (5, 1, 10),
                    'attack3': (3, 0, 11),
                }

                # Yes, we do have a joystick.
                self.joystick_found = True
                # Assigns a joystick to the corresponding index and initializes it.
                self.joystick = pygame.joystick.Joystick(index)
                self.joystick.init()
                # Not yet in use:
                # self.fishingrod = FishingRod(self.robot, b_angle=0)

                # Acquires the actual template of the joystick
                this_joystick = (self.joystick.get_numaxes(), self.joystick.get_numhats(), self.joystick.get_numbuttons())
                
                # Available joysticks: ADD NEW JOYSTICK KEYMAPS HERE!
                if this_joystick == available_templates.get('xbox'):
                    # XBOX Template:
                    # --- Buttons:
                    # A: 0
                    # B: 1
                    # X: 2
                    # Y: 3
                    # LB: 4
                    # RB: 5
                    # BACK: 6
                    # START: 7
                    # LDclick: 8
                    # RDclick: 9
                    # --- Axis:
                    # DL x: 0
                    # DL y: 1
                    # LT/RT: 2
                    # DR y: 3
                    # DR x: 4

                    self.chipkick_button = 4
                    self.kick_button = 5
                    self.dribble_button = 3
                    # if there's no need for a straffe, we set it as -1
                    self.straffe_button = -1
                    self.normal_axis = 1  # y
                    self.aux_axis = 0     # x
                    self.power_axis = 2   # power
                    self.straffe_axis = 5 # s
                    self.angle_axis = 4   # a
                elif this_joystick == available_templates.get('attack3'):
                    self.chipkick_button = 3
                    self.kick_button = 0
                    self.dribble_button = 2
                    self.straffe_button = 1
                    self.normal_axis = 1
                    self.aux_axis = 0
                    self.power_axis = 2
                else:
                    print 'ERROR: Unrecognized joystick template.'
            else:
                print 'ERROR: Joystick index not found.'

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

            # 'attack3-like' joysticks have straffe_button != -1
            if self.straffe_button != -1:
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

            # 'straffe-ready' joysticks have straffe_button == -1
            else:
                x = -self.joystick.get_axis(self.aux_axis)
                y = -self.joystick.get_axis(self.normal_axis)
                #s = self.joystick.get_axis(self.straffe_axis)
                a = -self.joystick.get_axis(self.angle_axis)
                power = abs(self.joystick.get_axis(self.power_axis))
                self.robot.action.speeds = y * self.speed_ratio, x * self.speed_ratio, a * 300

                if self.joystick.get_button(self.kick_button):
                    self.robot.action.kick = power
                elif self.joystick.get_button(self.chipkick_button):
                    self.robot.action.chipkick = power
                elif self.joystick.get_button(self.dribble_button):
                    self.robot.action.dribble = 1