from time import sleep

from ..base import Action, World
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

