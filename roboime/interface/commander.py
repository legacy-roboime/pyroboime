from math import pi

from ..communication.network import unicast
from ..communication import grsim
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
    def __init__(self, team, mapping_dict=None, ipaddr='192.168.91.105', port=9050, verbose=False, **kwargs):
        super(Tx2012Commander, self).__init__(**kwargs)
        self.default_map = mapping_dict is None
        self.mapping_dict = mapping_dict if mapping_dict is not None else keydefaultdict(lambda x: x)
        self.team = team
        self.verbose = verbose
        self.sender = unicast.UnicastSender(address=(ipaddr, port))

        # FIXME: These values should be on the robot prototype to allow for mixed-chassis teams. NOT HERE!

        # RoboIME 2013
        self.wheel_angles = [
            -1.0471975511965977461542144610932,
             1.0471975511965977461542144610932,
             2.3561944901923449288469825374596,
            -2.3561944901923449288469825374596,
        ]
 
        # RoboIME 2012
        #self.wheel_angles = [
        #    -0.99483767363676785884650373803851,
        #     0.99483767363676785884650373803851,
        #     2.3561944901923449288469825374596,
        #    -2.3561944901923449288469825374596,
        #]
        self.wheel_radius = 28.9;
        self.wheel_distance = 80.6;

    def omniwheel_speeds(self, theta, vx, vy, va):
        speeds = []
        for j in xrange(4):
            a = self.wheel_angles[j];
            val = cos(a) * (vy * cos(theta) - vx * sin(theta)) - sin(a) * (vx * cos(theta) + vy * sin(theta)) + va * self.wheel_distance
            val /= self.wheel_radius
            val /= 2 * pi
            speeds.append(val)
        return speeds

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
                string_list.extend([str(i) for i in self.omniwheel_speeds(a.robot.angle, vx, vy, va)])
                string_list.append(str((a.dribble or 0.0)))
                if a.kick > 0:
                    string_list.append(str((a.kick or 0.0)))
                    string_list.append('0')
                else:
                    string_list.append('0')
                    string_list.append(str((a.chipkick or 0.0)))
                a.reset()

            packet = ' '.join(string_list)
            if self.verbose: print packet
            if packet:
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
            if self.verbose: print packet
            if packet: 
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
