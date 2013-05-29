from sys import platform
if platform == 'win32':
    from multiprocessing.dummy import Process, Queue, Event, Lock
else:
    from multiprocessing import Process, Queue, Event, Lock
from . import updater
from . import commander
from . import filter


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


class Interface(Process):
    """ This class is used to manage a single interface channel

    More specifically, this class will instantiate a set of updaters,
    commanders and filters, and orchestrate them to interact with an
    instace of a World.
    """

    def __init__(self, world, updaters=[], commanders=[], filters=[], callback=lambda: None):
        """
        The callback function will be called whenever an update arrives,
        after the world is updated.
        """
        super(Interface, self).__init__()
        #self.updates = []
        #self.commands = []
        self.world = world
        self.updaters = updaters
        self.commanders = commanders
        self.filters = filters
        self.callback = callback
        self._exit = Event()

    def start(self):
        #super(Interface, self).start()
        for p in self.processes():
            p.start()

    def stop(self):
        for p in self.processes():
            p.stop()

    #def run(self):
    #    while not self._exit.is_set():
    #        for up in self.updaters:
    #            if not up.queue.empty():
    #                uu = up.queue.get()
    #                for fi in reversed(self.filters):
    #                    _uu = fi.filter_updates(uu)
    #                    if _uu is not None:
    #                        uu = _uu
    #                self.updates = uu

    #        for co in self.commanders:
    #            if self.actions is not None:
    #                co.send(self.actions)
    #            #co.send(actions)

    def step(self):
        #print "I'm stepping the interface."
        # updates injection phase
        for up in self.updaters:
            if not up.queue.empty():
                #uu = up.queue.get_nowait()
                for _ in xrange(15):
                    uu = up.queue.get()
                    if up.queue.empty():
                        break
                for fi in reversed(self.filters):
                    _uu = fi.filter_updates(uu)
                    if _uu is not None:
                        uu = _uu
                for u in uu:
                    u.apply(self.world)

            ##with up.queue_lock:
            ##    print 'Queue size: ', up.queue.qsize()
            #while not up.queue.empty() and count < 7:
            #    uu = up.queue.get()
            #    for fi in reversed(self.filters):
            #        _uu = fi.filter_updates(uu)
            #        if _uu is not None:
            #            uu = _uu
            #    for u in uu:
            #        u.apply(self.world)
            #    count += 1

            #if count > 0:
            #    self.callback()

        # actions extraction phase
        # TODO filtering
        for co in self.commanders:

            actions = []
            for r in co.team:
                if r.action is not None:
                    actions.append(r.action)
            for fi in self.filters:
                _actions = fi.filter_commands(actions)
                if _actions is not None:
                    actions = _actions

            #co.queue.put(actions)
            co.send(actions)

    def processes(self):
        for up in self.updaters:
            yield up
        #for co in self.commanders:
        #    yield co


class SimulationInterface(Interface):

    def __init__(self, world, filters=[], **kwargs):
        super(SimulationInterface, self).__init__(
            world,
            updaters=[updater.SimVisionUpdater()],
            commanders=[commander.SimCommander(world.blue_team), commander.SimCommander(world.yellow_team)],
            filters=filters + [filter.Speed(), filter.Scale()],
            **kwargs
        )

    #def start()
