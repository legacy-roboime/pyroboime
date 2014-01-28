from threading import Thread

from ..interface import SimulationInterface
from ..interface import TxInterface
from ..base import World, Yellow, Blue
from ..core import Dummy 
from ..core.plays import autoretaliate
from ..core.plays import stop


# Commands
# ========

# commands should be implemented like methods of the CLI class
# they should also be aware that possible arguments can only be strings
# furthermore anything returned should also be a string.


class Commands(object):
    """ 
    self is a reference to an instance of CLI, don't be fooled 

    Example:
    >>> Commands.use_sim_interface(CLI())
    """

    def __init__(self):
        raise NotImplementedError('This is what you get for trying to instance this class.')

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

    def set_default_mappings(self, team):
        """ Set id0: 0, id1: 1... for the team.
            Team is one of 'blue', 'yellow' """"
        pass

    def set_kick_power(self, team, r_id, power):
        """ Sets the kick power of a robot. """
        pass

    def set_firmware_id(self, team, r_id, firmware_id):
        """ Sets the firmware id of a robot. """
        pass

    def set_play(self, team, play_id):
        pass

    def set_individual(self, team, id, play_id):
        pass


class CLI(Thread):

    PLAY = 'play'
    INDIVIDUAL = 'individual'

    def __init__(self):
        super(CLI, self).__init__()
        self.quit = False
        self.world = World()

        self.run_mode = CLI.PLAY

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

        self.available_skills = {}
        self.available_tactics = {}
        self.available_plays = {}

        self.plays = { Yellow: Dummy(), Blue: Dummy() }
        self.tactics = { Yellow: [Dummy() for i in self.world.yellow_team], Blue: [Dummy() for i in self.world.blue_team] }
        self.skills = { Yellow: [Dummy() for i in self.world.yellow_team], Blue: [Dummy() for i in self.world.blue_team] }

        #TODO: remove this after test phase
        #self.plays['retaliate'] = autoretaliate.AutoRetaliate(self.world.yellow_team)
        #self.plays['stop1'] = stop.Stop(self.world.blue_team)


    def read(self):
        raise NotImplementedError('This is what you get for trying to instance an abstract class.')

    def write(self, text):
        raise NotImplementedError('This is what you get for trying to instance an abstract class.')

    def start(self):
        self.interface.start()
        super(CLI, self).start()

    def stop(self):
        self.interface.stop()

    def step(self):
        self.interface.step()
        if self.run_mode == CLI.PLAY:
            for p in self.plays.itervalues():
                p.step()
        if self.run_mode == CLI.TACTIC:
            for t in self.tactics.itervalues():
                t.step()
        if self.run_mode == CLI.SKILL:
            for s in self.skills.itervalues():
                s.step()

    def run(self):
        """
        Here lies the non-blocking code that will run on a different thread.
        The main purpose is to wait for input and iterpretate the given commands without blocking the main loop.
        """
        while True:
            try:
                cmdict = self.read()
                cmd, args = cmdict['cmd'], cmdict['args']

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
