#
# Copyright (C) 2013 RoboIME
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
from math import pi
import struct
import sys

#import socket
#from multiprocessing import Process, Queue, Event, Lock
from collections import defaultdict
from time import time
from math import isnan

from ..config import config
from ..communication import grsim
from ..communication.network import unicast
from ..utils.mathutils import sin, cos
from ..utils.keydefaultdict import keydefaultdict
from ..communication.rftransmission.vivatxrx import VIVATxRx


class Commander(object):
#class Commander(Process):
    """
    This class instantiates a process that receives the actions for the robots and
    dispatches its actions to the transmitter. As of now, this class does NOT
    implement potential field collision avoidance. This will be treated on a future
    release. When using this, an updater is needed to apply the updates that are coming
    both to the main window and to the Commander.

    It is still being decided whether or
    not this is going to be a thread in and of itself running in the main window
    """

    def __init__(self, team, maxsize=15):
        #self.world = World()
        #self.action_queue = Queue()
        super(Commander, self).__init__()
        #self._recvr, self._sendr = Pipe()
        #self.conn = None
        #self._exit = Event()
        self.team = team
        self.debug = config['interface']['debug']
        if self.debug:
            self._log = True
            if config['interface']['log-file'] == 'STDOUT':
                self._log_file = sys.stdout
            elif config['interface']['log-file'] == 'STDERR':
                self._log_file = sys.stderr
            else:
                self._log_file = open(config['interface']['log-file'], 'a')
        else:
            self._log = False
        pass

    def log(self, message):
       if self._log:
           self._log_file.write(str(message))
           self._log_file.write('\n')

    #def start(self):
    #    super(Commander, self).start()
    #    self.conn = self._sendr

    #def run(self):
    #    while self._exit.is_set():
    #        self.send(self.conn.recv())
    #    self.conn.close()

    #def stop(self):
    #    self.conn.close()
    #    self._exit.set()

    def send(self, actions):
        raise NotImplemented


class Tx2014Commander(Commander):
    """
    Sends commands as byte arrays via RF to the robots. Since the robots' firmware IDs are not the same as
    the UIDs sent by the VisionUpdater, a dict mapping the UIDs to the firmware IDs should be provided.
    If it is not provided, we shall use the trivial mapping: x => x.

    This commander uses a transmission protocol compatible with the RoboIME MK-2012/2013 architecture.
    The main difference from this one to the Tx2012Commander are that this one does not require
    the usage of a separate program to actually execute the radio transmission.
    """

    def __init__(self, team, mapping_dict=None, kicking_power_dict=None, **kwargs):
        super(Tx2014Commander, self).__init__(team, **kwargs)
        self.default_map = mapping_dict is None
        self.mapping_dict = mapping_dict if mapping_dict is not None else keydefaultdict(lambda x: x)
        self.kicking_power_dict = kicking_power_dict if kicking_power_dict is not None else defaultdict(lambda: 100)
        self.sender = VIVATxRx()

        # FIXME: These values should be on the robot prototype to allow for mixed-chassis teams. NOT HERE!
        self.wheel_angles = [
            +60.0,  # wheel 0
            +135.0, # wheel 1
            -135.0, # wheel 2
            -60.0,  # wheel 3
        ]

        # Values in meters.
        self.wheel_distance = 0.0850
        self.wheel_radius = 0.0289
        self.max_speed = 64.0

    def omniwheel_speeds(self, vx, vy, va):
        if isnan(vx) or isnan(vy) or isnan(va):
            return [0.0, 0.0, 0.0, 0.0]
        speeds = [(vy * cos(a) - vx * sin(a) + va * self.wheel_distance) / self.wheel_radius for a in self.wheel_angles]
        largest = max(abs(x) for x in speeds)
        if largest > self.max_speed:
            speeds = [x * self.max_speed / largest for x in speeds]
        return speeds

    def prepare_byte(self, x, max_speed=None):
        if max_speed == None:
            max_speed = self.max_speed
        if abs(x) > max_speed:
            x = x / abs(x)
        else:
            x = x / max_speed
        return int(127 * x) & 255

    def send(self, actions):
        actions_dict = keydefaultdict(lambda x: '\x7f\x00\x00\x00\x00\x00\x00')

        # Initializes packet with the header.
        has_action = False

        if len(actions) > 0:
            for a in actions:
                if not a:
                    continue
                has_action = True

                if a.has_speeds:
                    # this is the old move skill and default fallback

                    vx, vy, va = a.speeds
                    # Convert va to angular speed.
                    va = va * pi / 180

                    if self.default_map or a.uid in self.mapping_dict:
                        uid = self.mapping_dict[a.uid] | 128
                    else:
                        continue

                    s1, s2, s3, s4 = tuple(self.prepare_byte(-x) for x in self.omniwheel_speeds(vx, vy, va))
                    dribble = int((a.dribble or 0) * 255)

                    if a.kick > 0 and self.kicking_power_dict[a.uid] > 0:
                        kick = self.prepare_byte(a.kick * 100 / self.kicking_power_dict[a.uid] or 0.0, 1)
                    elif a.chipkick > 0 and self.kicking_power_dict[a.uid] > 0:
                        kick = self.prepare_byte(-a.chipkick * 100 / self.kicking_power_dict[a.uid] or 0.0, 1)
                    else:
                        kick = 0

                    robot_packet = struct.pack('!BBBBBBB', uid, s1, s2, s3, s4, dribble, kick)
                    actions_dict[self.mapping_dict[a.uid]] = robot_packet
                    a.reset()

                else:
                    # this is the goto skill that is now implemented in-robot

                    tx, ty, ta = a.target
                    robot_packet = struct.pack('<bHHH', self.mapping_dict[a.uid], 1000 * tx, 1000 * ty, 100 * ta)
                    actions_dict[self.mapping_dict[a.uid]] = robot_packet
                    a.reset()


            if has_action:
                # header [254, 0, 88]
                packet = '\xfe\x00\x58'
                for i in xrange(6):
                    packet += actions_dict[i]
                # tail [55]
                packet += '\x37'

                if self.debug:
                    self.log(' '.join(map(lambda i: '{:02x}'.format(i), map(ord, packet))))

                self.sender.send(packet)


class Tx2013Commander(Commander):
    """
    Sends commands as byte arrays via RF to the robots. Since the robots' firmware IDs are not the same as
    the UIDs sent by the VisionUpdater, a dict mapping the UIDs to the firmware IDs should be provided.
    If it is not provided, we shall use the trivial mapping: x => x.

    This commander uses a transmission protocol compatible with the RoboIME MK-2012/2013 architecture.
    The main difference from this one to the Tx2012Commander are that this one does not require
    the usage of a separate program to actually execute the radio transmission.
    """

    def __init__(self, team, mapping_dict=None, kicking_power_dict=None, **kwargs):
        super(Tx2013Commander, self).__init__(team, **kwargs)
        self.default_map = mapping_dict is None
        self.mapping_dict = mapping_dict if mapping_dict is not None else keydefaultdict(lambda x: x)
        self.kicking_power_dict = kicking_power_dict if kicking_power_dict is not None else defaultdict(lambda: 100)
        self.sender = VIVATxRx()

        # FIXME: These values should be on the robot prototype to allow for mixed-chassis teams. NOT HERE!
        self.wheel_angles = [
            +60.0,  # wheel 0
            +135.0, # wheel 1
            -135.0, # wheel 2
            -60.0,  # wheel 3
        ]

        # Values in meters.
        self.wheel_distance = 0.0850
        self.wheel_radius = 0.0289
        self.max_speed = 64.0

    def omniwheel_speeds(self, vx, vy, va):
        if isnan(vx) or isnan(vy) or isnan(va):
            return [0.0, 0.0, 0.0, 0.0]
        speeds = [(vy * cos(a) - vx * sin(a) + va * self.wheel_distance) / self.wheel_radius for a in self.wheel_angles]
        largest = max(abs(x) for x in speeds)
        if largest > self.max_speed:
            speeds = [x * self.max_speed / largest for x in speeds]
        return speeds

    def prepare_byte(self, x, max_speed=None):
        if max_speed == None:
            max_speed = self.max_speed
        if abs(x) > max_speed:
            x = x / abs(x)
        else:
            x = x / max_speed
        return int(127 * x) & 255

    def send(self, actions):
        actions_dict = keydefaultdict(lambda x: [x | 128, 0, 0, 0, 0, 0, 0])

        # Initializes packet with the header.
        has_action = False

        if len(actions) > 0:
            for a in actions:
                if not a:
                    continue
                has_action = True
                vx, vy, va = a.speeds
                # Convert va to angular speed.
                va = va * pi / 180
                robot_packet = []

                if self.default_map or a.uid in self.mapping_dict:
                    robot_packet.append(self.mapping_dict[a.uid])
                else:
                    continue
                #if a.uid == 3:
                #    print self.omniwheel_speeds(vx, vy, va)
                robot_packet.extend([self.prepare_byte(-x) for x in self.omniwheel_speeds(vx, vy, va)])
                robot_packet.append(int((a.dribble or 0) * 255))
                if a.kick > 0 and self.kicking_power_dict[a.uid] > 0:
                    robot_packet.append(self.prepare_byte(a.kick * 100 / self.kicking_power_dict[a.uid] or 0.0, 1))
                elif a.chipkick > 0 and self.kicking_power_dict[a.uid] > 0:
                    robot_packet.append(self.prepare_byte(-a.chipkick * 100 / self.kicking_power_dict[a.uid] or 0.0, 1))
                else:
                    robot_packet.append(0)

                actions_dict[self.mapping_dict[a.uid]] = robot_packet
                #a.reset()

            if has_action:
                packet = [254, 0, 44]
                for i in xrange(6):
                    packet.extend(actions_dict[i])
                packet.append(55)
                if packet:
                    if self.debug:
                        self.log('|'.join('{:03d}'.format(x) for x in packet))
                    #print '|'.join('{:03d}'.format(x) for x in packet)
                    self.sender.send(packet)


class Tx2012Commander(Commander):
    """
    Sends commands as strings via unicast UDP to the C# transmitter process that will dispatch commands
    via RF to the robots. Since the robots' firmware IDs are not the same as the UIDs sent by the
    VisionUpdater, a dict mapping the UIDs to the firmware IDs should be provided. If it is not provided,
    we shall use the trivial mapping: x => x.

    This commander uses a transmission protocol compatible with the RoboIME MK-2012 architecture.
    This might be deprecated soon. Or not.
    """

    def __init__(self, team, mapping_dict=None, kicking_power_dict=None, ipaddr='127.0.0.1', port=9050, **kwargs):
        super(Tx2012Commander, self).__init__(team, **kwargs)
        self.default_map = mapping_dict is None
        self.mapping_dict = mapping_dict if mapping_dict is not None else keydefaultdict(lambda x: x)
        self.kicking_power_dict = kicking_power_dict if kicking_power_dict is not None else defaultdict(lambda: 100)
        self.sender = unicast.UnicastSender(address=(ipaddr, port))
        #self.sock = so
        # FIXME: These values should be on the robot prototype to allow for mixed-chassis teams. NOT HERE!

        # RoboIME 2013
        #self.wheel_angles = [
        #    -60.,
        #    +60.,
        #    +135.,
        #    -135.,
        #]
        # RoboIME 2013
        self.wheel_angles = [
            -45.0,
            +45.0,
            +120.0,
            -120.0,
        ]

        # RoboIME 2012
        #self.wheel_angles = [
        #    -57.,
        #    +57.,
        #    +135.,
        #    -135.,
        #]
        #self.wheel_radius = 28.9
        #self.wheel_distance = 80.6

        #Values in meters.
        self.wheel_radius = 0.0289
        self.wheel_distance = 0.0806

    def omniwheel_speeds(self, vx, vy, va):
        return [(vy * cos(a) - vx * sin(a) + va * self.wheel_distance) / self.wheel_radius for a in self.wheel_angles]

    def send(self, actions):
        actions_dict = defaultdict(lambda:['0', '0', '0', '0', '0', '0', '0'])
        has_action = False
        if len(actions) > 0:
            for a in actions:
                string_list = []
                if not a:
                    continue
                has_action = True
                vx, vy, va = a.speeds
                # Convert va to angular speed.
                va = va * pi / 180
                if self.default_map or a.uid in self.mapping_dict:
                    pass
                    #string_list.append(str(self.mapping_dict[a.uid]))
                else:
                    continue

                string_list.extend([str(i) for i in self.omniwheel_speeds(vx, vy, -va)])
                string_list.append(str((a.dribble or 0.0)))
                if a.kick > 0 and self.kicking_power_dict[a.uid] > 0:
                    string_list.append(str((a.kick * 100 / self.kicking_power_dict[a.uid] or 0.0)))
                    #string_list.append(str((a.kick or 0.0)))
                    string_list.append('0')
                elif a.chipkick > 0 and self.kicking_power_dict[a.uid] > 0:
                    string_list.append('0')
                    string_list.append(str((a.chipkick * 100 / self.kicking_power_dict[a.uid] or 0.0)))
                    #string_list.append(str((a.chipkick or 0.0)))
                else:
                    string_list.append('0')
                    string_list.append('0')

                actions_dict[self.mapping_dict[a.uid]] = string_list
                a.reset()
            if has_action:
                string_list = []
                for i in xrange(6):
                    string_list.extend(actions_dict[i])

                packet = ' '.join(string_list)

                if packet:
                    #if self.debug:
                    #    # print self.kicking_power_dict
                    #    print packet
                    self.sender.send(packet)


class SimCommander(Commander):

    def __init__(self, team, address, send_omni=True, **kwargs):
        super(SimCommander, self).__init__(team, **kwargs)
        self.sender = grsim.grSimSender(address)
        self.send_omni = send_omni

        # FIXME: These values should be on the robot prototype to allow for mixed-chassis teams. NOT HERE!
        self.wheel_angles = [
            +60.0,  # wheel 0
            +135.0, # wheel 1
            -135.0, # wheel 2
            -60.0,  # wheel 3
        ]
        self.wheel_distance = 0.0850
        self.wheel_radius = 0.0289

    def omniwheel_speeds(self, vx, vy, va):
        if isnan(vx) or isnan(vy) or isnan(va):
            return [0.0, 0.0, 0.0, 0.0]
        return [(vy * cos(a) - vx * sin(a) + va * self.wheel_distance) / self.wheel_radius for a in self.wheel_angles]

    def send(self, actions):
        packet = self.sender.new_packet()

        if len(actions) > 0:
            packet.commands.isteamyellow = self.team.is_yellow
            packet.commands.timestamp = time()
            for a in actions:
                if not a:
                    continue
                vx, vy, va = a.speeds
                c = packet.commands.robot_commands.add()
                c.id = a.uid
                chip_angle = 45
                c.kickspeedz = (a.chipkick or 0.0) * sin(chip_angle)
                if c.kickspeedz > 0:
                    # XXX FIXME this should be tested,
                    # we don't know at what angle we
                    # will be able to chipkick
                    c.kickspeedx = a.chipkick * cos(chip_angle)
                else:
                    c.kickspeedx = (a.kick or 0.0) * 5
                c.veltangent = vx
                c.velnormal = vy
                c.velangular = va * pi / 180
                c.spinner = (a.dribble or 0.0) > 0
                c.wheelsspeed = False
                if self.send_omni:
                    c.wheelsspeed = True
                    speeds = self.omniwheel_speeds(vx, vy, va * pi / 180)
                    c.wheel1 = speeds[0]
                    c.wheel2 = speeds[1]
                    c.wheel3 = speeds[2]
                    c.wheel4 = speeds[3]

                # reset action values
                a.reset()

        #print packet
        self.sender.send_packet(packet)
