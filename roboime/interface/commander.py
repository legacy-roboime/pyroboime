from math import pi

#import socket
from ..communication.network import unicast
from ..communication import grsim
from collections import defaultdict
from time import time

from ..utils.mathutils import sin, cos
from ..utils.keydefaultdict import keydefaultdict


class Commander(object):
#class Commander(Process):

    def __init__(self):
        #super(Commander, self).__init__()
        #self._recvr, self._sendr = Pipe()
        #self.conn = None
        #self._exit = Event()
        pass

    #def start(self):
    #    super(Commander, self).start()
    #    self.conn = self._sendr

    #def run(self):
    #    self.conn = self._recvr
    #    while self._exit.is_set():
    #        self.send(self.conn.recv())
    #    self.conn.close()

    #def stop(self):
    #    self.conn.close()
    #    self._exit.set()

    def send(self, actions):
        raise NotImplemented


class Tx2012Commander(Commander):
    '''
    Sends commands as strings via unicast UDP to the C# transmitter process that will dispatch commands
    via RF to the robots. Since the robots' firmware IDs are not the same as the UIDs sent by the
    VisionUpdater, a dict mapping the UIDs to the firmware IDs should be provided. If it is not provided,
    we shall use the trivial mapping: x => x.

    This commander uses a transmission protocol compatible with the RoboIME MK-2012 architecture.
    This might be deprecated soon. Or not.
    '''
    def __init__(self, team, mapping_dict=None, kicking_power_dict=None, ipaddr='127.0.0.1', port=9050, verbose=False, **kwargs):
        super(Tx2012Commander, self).__init__(**kwargs)
        self.default_map = mapping_dict is None
        self.mapping_dict = mapping_dict if mapping_dict is not None else keydefaultdict(lambda x: x)
        self.kicking_power_dict = kicking_power_dict if kicking_power_dict is not None else defaultdict(lambda: 100)
        self.team = team
        self.verbose = verbose
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
            -45.,
            +45.,
            +120.,
            -120.,
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
        self.wheel_radius = .0289
        self.wheel_distance = .0806

    def omniwheel_speeds(self, vx, vy, va):
        return [(vy * cos(a) - vx * sin(a) + va * self.wheel_distance) / self.wheel_radius for a in self.wheel_angles]

    def send(self, actions):
        actions_dict = defaultdict(lambda:['0','0','0','0','0','0','0'])
        dirty = False
        if len(actions) > 0:
            for a in actions:
                string_list = []
                if not a:
                    continue
                dirty = True
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
                    string_list.append(str((a.chipkick * 100 /self.kicking_power_dict[a.uid] or 0.0)))
                    #string_list.append(str((a.chipkick or 0.0)))
                else:
                    string_list.append('0')
                    string_list.append('0')

                actions_dict[self.mapping_dict[a.uid]] = string_list
                a.reset()
            if dirty:
                string_list = []
                for i in xrange(6):
                    string_list.extend(actions_dict[i])

                packet = ' '.join(string_list)

                if packet:
                    if self.verbose:
                        pass#print self.kicking_power_dict
                        print packet
                    self.sender.send(packet)


class TxCommander(Commander):
    '''
    Sends commands as strings via unicast UDP to the C# transmitter process that will dispatch commands
    via RF to the robots. Since the robots' firmware IDs are not the same as the UIDs sent by the
    VisionUpdater, a function mapping the UIDs to the firmware IDs should be provided. If it is not provided,
    we shall use the trivial mapping: x => x.

    This commander uses the transmission protocol for the RoboIME MK-2013 architecture.

    Main differences are:

    - Not passing wheel velocities directly, sending instead the triplet vx, vy, theta;
    - Chip kick.
    '''
    def __init__(self, team, mapping_dict=None, ipaddr='127.0.0.1', port=9050, verbose=False, **kwargs):
        super(TxCommander, self).__init__(**kwargs)
        self.default_map = mapping_dict is None
        self.mapping_dict = mapping_dict if mapping_dict is not None else keydefaultdict(lambda x: x)
        self.team = team
        self.verbose = verbose
        self.sender = unicast.UnicastSender(address=(ipaddr, port))

    def send(self, actions):
        string_list = []
        if len(actions) > 0:
            for a in actions:
                if not a:
                    continue
                vx, vy, va = a.speeds

                if self.default_map or a.uid in self.mapping_dict:
                    string_list.append(str(self.mapping_dict[a.uid]))
                else:
                    continue

                string_list.append(str((a.robot.angle or 0.0)))
                string_list.append(str((vx or 0.0)))
                string_list.append(str((vy or 0.0)))
                string_list.append(str((va or 0.0)))
                string_list.append(str((a.dribble or 0.0)))
                string_list.append(str((a.kick or 0.0)))
                string_list.append(str((a.chipkick or 0.0)))
                a.reset()

            packet = ' '.join(string_list)
            if packet:
                if self.verbose:
                    print packet
                self.sender.send(packet)


class SimCommander(Commander):

    def __init__(self, team, **kwargs):
        super(SimCommander, self).__init__(**kwargs)
        self.team = team
        #self.sender = grsim.grSimSender(('200.20.120.133', 20011))
        self.sender = grsim.grSimSender()

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

                # reset action values
                a.reset()

        #print packet
        self.sender.send_packet(packet)
