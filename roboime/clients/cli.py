from threading import Thread
from collections import defaultdict

from ..interface import SimulationInterface
from ..interface import TxInterface
from ..base import World, Yellow, Blue
from ..core import Dummy 
from ..core.skills import goto
from ..core.skills import gotoavoid
from ..core.skills import drivetoobject
from ..core.skills import drivetoball
from ..core.skills import sampleddribble
from ..core.skills import sampledkick
from ..core.skills import followandcover
from ..core.skills import sampledchipkick
from ..core.skills import kickto
try:
    from ..core.skills import joystick
except ImportError:
    joystick = None
from ..core.tactics import blocker
from ..core.tactics import defender
from ..core.tactics import goalkeeper
from ..core.tactics import zickler43
from ..core.tactics import executepass
from ..core.tactics import receivepass
from ..core.plays import autoretaliate
from ..core.plays import indirectkick
from ..core.plays import stop
from ..core.plays import obeyreferee
from ..core.plays import halt
from ..core.plays import ifrit


# Commands
# ========

# commands should be aware that possible arguments can only be strings
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
        self.interface = TxInterface(self.world,
                                     mapping_yellow=self.id_mapping[Yellow],
                                     mapping_blue=self.id_mapping[Blue],
                                     kick_mapping_yellow=self.kick_mapping[Yellow],
                                     kick_mapping_blue=self.kick_mapping[Blue])
        self.interface.start()

    def set_default_mappings(self, team):
        """ Set id0: 0, id1: 1... for the team.
            Team is one of base.Blue, base.Yellow """
        for i in xrange(10):
            self.id_mapping[team][i] = i;
        return "OK"

    def set_kick_power(self, team, r_id, power):
        """ Sets the kick power of a robot. """
        self.kick_mapping[team][r_id] = power


    def set_firmware_id(self, team, r_id, firmware_id):
        """ Sets the firmware id of a robot. """
        self.id_mapping[team][r_id] = firmware_id

    def set_play(self, team, play_id):
        self.plays[team] = self.available_plays[play_id](self.world.team(team))

    def set_individual(self, team, r_id, play_id):
        self.individuals[team] = self.available_individuals[play_id](self.world.team(team)[r_id])



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

        # Magic
        commands = filter(lambda i: not i.startswith('_'), dir(Commands))

        self.cmd_dict = { i: getattr(Commands, i) for i in commands }
        print self.cmd_dict

        self.available_individuals = lambda robot: OrderedDict([
            ('', Dummy()),
            ('Go To', goto.Goto(robot, target=Point(0, 0))),
            ('Go To Avoid', gotoavoid.GotoAvoid(robot, target=Point(0, 0), avoid=self.world.ball)),
            ('Drive To Object', drivetoobject.DriveToObject(robot, lookpoint=robot.enemy_goal, point=self.world.ball)),
            ('Drive To Ball', drivetoball.DriveToBall(robot, lookpoint=robot.enemy_goal)),
            ('Sampled Dribble', sampleddribble.SampledDribble(robot, lookpoint=robot.enemy_goal)),
            ('Sampled Kick', sampledkick.SampledKick(robot, lookpoint=robot.enemy_goal)),
            ('Follow And Cover', followandcover.FollowAndCover(robot, follow=robot.goal, cover=self.world.ball)),
            ('Sampled Chip Kick', sampledchipkick.SampledChipKick(robot, lookpoint=robot.enemy_goal)),
            ('Kick To (0,0)', kickto.KickTo(robot, lookpoint=Point(0, 0))),
            ('Blocker', blocker.Blocker(robot, arc=0)),
            ('Goalkeeper', goalkeeper.Goalkeeper(robot, angle=30, aggressive=True)),
            ('Zickler43', zickler43.Zickler43(robot)),
            ('Defender', defender.Defender(robot, enemy=self.world.ball)),
            ('Dummy Receive Pass', receivepass.ReceivePass(robot, Point(0,0))),
            ('Joystick', joystick.Joystick(robot)) if joystick is not None else dummy,
        ])

        self.available_plays = lambda team: OrderedDict([
            ('', Dummy()),
            ('Auto Retaliate', autoretaliate.AutoRetaliate(team)),
            ('Ifrit', ifrit.Ifrit(team)),
            ('Stop', stop.Stop(team)),
            ('Indirect Kick', indirectkick.IndirectKick(team)),
            ('Obey Referee', obeyreferee.ObeyReferee(autoretaliate.AutoRetaliate(team))),
            ('Halt', halt.Halt(team)),
        ])

        self.id_mapping = { Blue: {}, Yellow: {} }
        self.kick_mapping = { Blue: defaultdict(lambda: 100), Yellow: defaultdict(lambda: 100) }

        self.plays = { Yellow: Dummy(), Blue: Dummy() }
        self.individuals = { Yellow: [Dummy() for i in self.world.yellow_team], Blue: [Dummy() for i in self.world.blue_team] }


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
        if self.run_mode == CLI.INDIVIDUAL:
            for l in self.individuals.itervalues():
                for t in l:
                    t.step()

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
