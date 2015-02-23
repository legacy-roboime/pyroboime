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
from time import sleep

from ..base import World
from ..interface.commander import SimCommander
from ..interface.updater import SimVisionUpdater

#TODO: do real tests
world = World()
updater = SimVisionUpdater(world)
commander = SimCommander(world.blue_team)


def basicloop(times=100, delay=10):
    """times: how many cicles?, delay: cicle time in ms."""
    #setup
    #wolrd = World()

    #test action
    a = world.blue_team[2].action
    a.x = -2.5
    a.y = 1.5
    a.angle = 30.0

    #the loop
    for _ in xrange(times):
        updater.step()
        sleep(delay / 1000.0)
        commander.step()
