from . import updater
from . import commander


def _update_loop(queue, updater):
    while True:
        queue.put(updater.receive())


def _command_loop(queue, commander):
    latest_actions = None
    while True:
        while not queue.empty():
            latest_actions = queue.get()
        if latest_actions is not None:
            commander.send(latest_actions)


class Interface(object):
    """ This class is used to manage a single interface channel

    More specifically, this class will instantiate a set of updaters,
    commanders and filters, and orchestrate them to interact with an
    instace of a World.
    """

    def __init__(self, world, updaters, commanders, filters):
        self.world = world
        self.updaters = updaters
        self.commanders = commanders
        self.filters = filters

    def start(self):
        for p in self.processes:
            p.start()

    def stop(self):
        for p in self.processes:
            p.stop()

    def step(self):
        # updates injection fase
        # TODO filtering
        for up in self.updaters:
            while not up.queue.empty():
                for u in up.queue.get():
                    u.apply(self.world)

        # actions extraction fase
        # TODO filtering
        for co in self.commanders:
            actions = []
            for r in co.team:
                if r.action is not None:
                    actions.append(r.action)
            #co.queue.put(actions)
            co.send(actions)

    @property
    def processes(self):
        for up in self.updaters:
            yield up
        #for co in self.commanders:
        #    yield co

    #def __del__(self):
    #    self.stop()
    #    #for p in self.updaters:
    #    #    if p.is_alive():
    #    #        print 'Killing process', p
    #    #        p.terminate()


class SimulationInterface(Interface):

    def __init__(self, world, filters=[]):
        updaters = [updater.SimVisionUpdater()]
        commanders = [commander.SimCommander(world.blue_team), commander.SimCommander(world.yellow_team)]
        #self._updaters
        Interface.__init__(self, world, updaters, commanders, filters)

    #def start()
