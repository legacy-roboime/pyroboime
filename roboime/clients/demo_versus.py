#
# Copyright (C) 2013-2015 RoboIME
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
from ..core.plays import stop
from ..core.tactics import goalkeeper
from ..core.tactics import blocker
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

        if config['demo']['stop'] == False:
            self.stuff['atk'] = zickler.Zickler43(self.world.yellow_team[1])
            self.stuff['joy'] = joystick.Joystick(self.world.yellow_team[2])
        else:
            self.stuff['bl1'] = blocker.Blocker(self.world.yellow_team[1], arc=23., distance=0.25)
            self.stuff['bl2'] = blocker.Blocker(self.world.yellow_team[2], arc=-23., distance=0.25)

    def loop(self):

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
