from time import sleep

from ..base import Action, Field
from ..interface.commander import SimCommander
from ..interface.updater import SimVisionUpdater

#TODO: do real tests

def basicloop(times, delay):
    #setup
    field = Field()
    updater = SimVisionUpdater(field)
    commander = SimCommander(field.blue_team)

    #test action
    a = Action(2, 2, 2)
    field.blue_team[2].action = a

    #the loop
    for _ in xrange(times):
        updater.step()
        commander.step()
        sleep(delay)

