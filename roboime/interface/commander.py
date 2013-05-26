from multiprocessing import Process, Queue, Event
from math import pi

from ..communication import grsim
from time import time


class Commander(Process):
#class Commander(object):

    def __init__(self):
        #Process.__init__(self)
        self.queue = Queue()
        self._exit = Event()

    def run(self):
        while self._exit.is_set():
            try:
                self.send(self.queue.get())
            except KeyboardInterrupt:
                break

    def stop(self):
        self._exit.set()

    def sendall(self, actions):
        while not actions.empty():
            self.send(actions.get())

    def send(self, actions):
        pass


class SimCommander(Commander):

    def __init__(self, team):
        Commander.__init__(self)
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
                c.kickspeedz = (a.chipkick or 0.0) * 3
                if c.kickspeedz > 0:
                    # XXX FIXME this should be tested,
                    # we don't know at what angle we
                    # will be able to chipkick
                    c.kickspeedx = 1.5 * c.kickspeedz
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
