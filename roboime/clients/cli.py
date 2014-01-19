from threading import Thread

from ..interface import SimulationInterface
from ..interface import TxInterface
from ..base import World
from ..core.plays import autoretaliate
from ..core.plays import stop


# Commands
# ========

# commands should be implemented like methods of the CLI class
# they should also be aware that possible arguments can only be strings
# furthermore anything returned should also be a string.


def use_sim_interface(self):
    """Switch to interfacing with the simnulator."""
    self.interface.stop()
    self.interface = SimulationInterface(self.world)
    self.interface.start()


def use_real_interface(self):
    """Switch to interfacing with the transmission."""
    self.interface.stop()
    self.interface = TxInterface(self.world)
    self.interface.start()


class CLI(Thread):

    def __init__(self):
        super(CLI, self).__init__()
        self.quit = False
        self.world = World()

        # initial interface:
        self.interface = SimulationInterface(self.world)
        #self.interface = TxInterface(self.world)

        self.commands = [
            use_sim_interface,
            use_real_interface,
        ]

        # assemble a dict mapped by the function names
        # could be used to assemble aliases, but those are a waste of time
        self.cmd_dict = dict((c.func_name, c) for c in self.commands)

        self.skills = {}
        self.tactics = {}
        self.plays = {}

        #TODO: remove this after test phase
        self.plays['retaliate'] = autoretaliate.AutoRetaliate(self.world.yellow_team)
        self.plays['stop1'] = stop.Stop(self.world.blue_team)

    def read(self):
        raise NotImplementedError('this method is meant to be overridden')

    def write(self, text):
        raise NotImplementedError('this method is meant to be overridden')

    def start(self):
        self.interface.start()
        super(CLI, self).start()

    def stop(self):
        self.interface.stop()

    def step(self):
        self.interface.step()
        for p in self.plays.itervalues():
            p.step()
        for t in self.tactics.itervalues():
            t.step()
        for s in self.skills.itervalues():
            s.step()

    def run(self):
        """
        Here lies the non-blocking code that will run on a different thread.
        The main purpose is to wait for input and iterpretate the given commands without blocking the main loop.
        """
        while True:
            try:
                raw_cmd = self.read().split() or ['']
                cmd, args = raw_cmd[0], raw_cmd[1:]

                if cmd == 'q' or cmd == 'quit' or cmd == 'exit':
                    # quit is special because it breaks the loop
                    self.quit = True
                    self.write('Bye...')
                    break
                else:
                    if cmd in self.cmd_dict:
                        self.write(self.cmd_dict[cmd](self, *args) or '')
                    else:
                        self.write('Command {} not recognized.'.format(cmd))

            except Exception as e:
                self.write('An exception occured: {}\nQuiting...'.format(e))
                self.quit = True
                break

    def mainloop(self):
        try:
            self.start()
            while True:
                self.step()
                if self.quit:
                    self.stop()
                    break
        except KeyboardInterrupt:
            self.stop()
