from time import time

from ..base import World
from ..interface import SimulationInterface
#from ..interface import TxInterface
from ..core.tactics import goalkeeper
from ..core.tactics import zickler43 as zickler
from ..core.skills import joystick


class Demo(object):
    """
    This is a simple example with no graphical interface.
    """

    def __init__(self):
        self.world = World()
        self.interface = SimulationInterface(self.world)
        #self.interface = TxInterface(self.world)
        self.stuff = {}

    def loop(self):
        if 0 in self.world.blue_team and 'attacker' not in self.stuff:
            r = self.world.blue_team[0]
            self.stuff['attacker'] = zickler.Zickler43(r)

        if 0 in self.world.yellow_team and 'joystick' not in self.stuff:
            r = self.world.yellow_team[0]
            self.stuff['joystick'] = joystick.Joystick(r)

        if 1 in self.world.blue_team and 'goalkeeper1' not in self.stuff:
            r = self.world.blue_team[1]
            self.stuff['goalkeeper1'] = goalkeeper.Goalkeeper(r)

        if 1 in self.world.yellow_team and 'goalkeeper2' not in self.stuff:
            r = self.world.yellow_team[1]
            self.stuff['goalkeeper2'] = goalkeeper.Goalkeeper(r)

        for s in self.stuff.itervalues():
            s.step()

        self.interface.step()

    def mainloop(self):
        self.interface.start()
        self.t0 = time()
        try:
            while True:
                self.loop()
        except KeyboardInterrupt:
            self.interface.stop()
