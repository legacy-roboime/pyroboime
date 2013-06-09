from math import pi

from ..communication import grsim
from time import time

from ..utils.mathutils import sin, cos

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
