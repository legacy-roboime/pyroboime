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
from time import time

from ..base import World
from ..interface import SimulationInterface
from ..interface import TxInterface
from ..core.tactics import goalkeeper
from ..core.tactics import zickler43 as zickler
from ..core.skills import joystick
from ..config import config


class Demo(object):
    """
    This is a simple example with no graphical interface.
    """

    def __init__(self):
        self.world = World()
        if config['interface']['default'] == 'sim':
            self.interface = SimulationInterface(self.world)
        elif config['interface']['default'] == 'tx':
            self.interface = TxInterface(self.world, command_blue=False)
        self.stuff = {}

    def loop(self):
        if 0 in self.world.blue_team and 'attacker' not in self.stuff:
            r = self.world.blue_team[1]
            self.stuff['attacker'] = zickler.Zickler43(r)

        if 0 in self.world.yellow_team and 'joystick' not in self.stuff:
            r = self.world.yellow_team[1]
            self.stuff['joystick'] = joystick.Joystick(r)

        if 1 in self.world.blue_team and 'goalkeeper1' not in self.stuff:
            r = self.world.blue_team[0]
            self.stuff['goalkeeper1'] = goalkeeper.Goalkeeper(r)

        if 1 in self.world.yellow_team and 'goalkeeper2' not in self.stuff:
            r = self.world.yellow_team[0]
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
