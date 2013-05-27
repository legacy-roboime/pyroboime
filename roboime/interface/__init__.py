# These imports are here so that one doesn't need PyQt to run the CLI client.
try:
    from PyQt4.QtCore import QObject, pyqtSignal
except: 
    class QObject(object):
        pass

    class pyqtSignal(object):
       def __init__(self, *args, **kwargs):
            pass
    
       def emit(*args, **kwargs):
            pass

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


class Interface(QObject):
    """ This class is used to manage a single interface channel

    More specifically, this class will instantiate a set of updaters,
    commanders and filters, and orchestrate them to interact with an
    instace of a World.
    """

    world_updated = pyqtSignal()

    def __init__(self, world, updaters, commanders, filters):
        super(Interface, self).__init__()
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
        #print "I'm stepping the interface."
        # updates injection phase
        for up in self.updaters:
            count = 0
            #with up.queue_lock:
            #    print 'Queue size: ', up.queue.qsize()
            while not up.queue.empty() and count < 7:
                uu = up.queue.get()
                for fi in reversed(self.filters):
                    _uu = fi.filter_updates(uu)
                    if _uu is not None:
                        uu = _uu
                for u in uu:
                    u.apply(self.world)
                    print 'emitting signal'
                    self.world_updated.emit()
                count = count + 1



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
            co.queue.put(actions)
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
        filters = filters + [filter.Speed(), filter.Scale()]
        Interface.__init__(self, world, updaters, commanders, filters)

    #def start()
