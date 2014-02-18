#
# Copyright (C) 2013 RoboIME
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
from threading import Thread
from collections import defaultdict
from collections import OrderedDict
from ..utils.geom import Point

from ..interface import SimulationInterface
from ..interface import TxInterface
from ..base import World
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
#from ..core.tactics import executepass
from ..core.tactics import receivepass
from ..core.plays import autoretaliate
from ..core.plays import indirectkick
from ..core.plays import stop
from ..core.plays import obeyreferee
from ..core.plays import halt
from ..core.plays import ifrit
from ..config import config

_individuals = {
    'dummy': lambda r: Dummy(),
    'goto': lambda r: goto.Goto(r, target=Point(0, 0)),
    'goto_avoid': lambda r: gotoavoid.GotoAvoid(r, target=Point(0, 0), avoid=r.world.ball),
    'drive_to_object': lambda r: drivetoobject.DriveToObject(r, lookpoint=r.enemy_goal, point=r.world.ball),
    'drive_to_ball': lambda r: drivetoball.DriveToBall(r, lookpoint=r.enemy_goal),
    'sampled_driblle': lambda r: sampleddribble.SampledDribble(r, lookpoint=r.enemy_goal),
    'sampled_kick': lambda r: sampledkick.SampledKick(r, lookpoint=r.enemy_goal),
    'follow_and_cover': lambda r: followandcover.FollowAndCover(r, follow=r.goal, cover=r.world.ball),
    'sampled_chip_kick': lambda r: sampledchipkick.SampledChipKick(r, lookpoint=r.enemy_goal),
    'kick_to': lambda r: kickto.KickTo(r, lookpoint=Point(0, 0)),
    'blocker': lambda r: blocker.Blocker(r, arc=0),
    'goalkeeper': lambda r: goalkeeper.Goalkeeper(r, angle=30, aggressive=True),
    'zickler43': lambda r: zickler43.Zickler43(r),
    'defender': lambda r: defender.Defender(r, enemy=r.world.ball),
    'dummy_receive_pass': lambda r: receivepass.ReceivePass(r, Point(0,0)),
}
if joystick is not None:
    _individuals['joystick'] = lambda r: joystick.Joystick(r)

_plays = {
    'dummy': lambda t: Dummy(),
    'halt': lambda t: halt.Halt(t),
    'stop': lambda t: stop.Stop(t),
    'auto_retaliate': lambda t: autoretaliate.AutoRetaliate(t),
    'indirect_kick': lambda t: indirectkick.IndirectKick(t),
    'ifrit': lambda t: ifrit.Ifrit(t),
    'obey': lambda t: obeyreferee.ObeyReferee(autoretaliate.AutoRetaliate(t)),
}

def _get_team(self, team):
    if team == 'blue':
        return self.world.blue_team
    elif team == 'yellow':
        return self.world.yellow_team

def _get_robot(self, team, robot):
    t = _get_team(self, team)
    if t is not None:
        return t[int(robot)]

# Commands
# ========


class _commands(object):
    """This class is not to be used directly"""
    # commands should be aware that possible arguments can only be strings
    # furthermore should you need to output something use self.write
    # in all cases self is an instance of CLI, don't be fooled

    def __init__(self):
        raise NotImplementedError('This is what you get for trying to instance this class.')

    def use_sim_interface(self):
        """use the simulator interface"""
        self.interface.stop()
        self.interface = SimulationInterface(self.world)
        self.interface.start()
        self.write('ok')

    def use_real_interface(self):
        """use the real interface"""
        self.interface.stop()
        self.interface = TxInterface(
            self.world,
            mapping_yellow=self.id_mapping["yellow"],
            mapping_blue=self.id_mapping["blue"],
            kick_mapping_yellow=self.kick_mapping["yellow"],
            kick_mapping_blue=self.kick_mapping["blue"],
        )
        self.interface.start()
        self.write('ok')

    def set_default_mappings(self, team):
        """set_default_mappings <blue|yellow>
        this is only used for the real interface
        """
        for i in xrange(10):
            self.id_mapping[team][i] = i;
        self.write('ok')

    def set_kick_power(self, team, robot, power):
        """set_kick_power <blue|yellow> robot power
        this is only used for the real interface
        """
        self.kick_mapping[team][int(robot)] = float(power)
        self.write('ok')

    def set_firmware_id(self, team, robot, firmware_id):
        """set_firmware_id <blue|yellow> robot firmware_id
        this is only used for the real interface
        """
        self.id_mapping[team][int(robot)] = int(firmware_id)
        self.write('ok')

    def halt(self):
        """halts both teams, resets all individuals"""
        self.plays['blue'] = _plays['halt'](self.world.blue_team)
        self.plays['yellow'] = _plays['halt'](self.world.yellow_team)
        for indv in self.individuals.itervalues():
            for i in indv:
                indv[i] = Dummy()
        self.write('ok')

    def stop(self):
        """stops both teams, resets all individuals"""
        #XXX: let the previous be gc'ed?
        self.plays['blue'] = _plays['stop'](self.world.blue_team)
        self.plays['yellow'] = _plays['stop'](self.world.yellow_team)
        for indv in self.individuals.itervalues():
            for i in indv:
                indv[i] = Dummy()
        self.write('ok')

    def plays(self):
        """list available plays"""
        self.write('\n'.join(_plays.keys()))

    def individuals(self):
        """list available individuals"""
        self.write('\n'.join(_individuals.keys()))

    def set_play(self, team, play):
        """set_play <blue|yellow> play"""
        if play in _plays:
            self.plays[team] = _plays[play](_get_team(self, team))
            self.write('ok')
        else:
            self.write('play {} does not exist'.format(play), ok=False)

    def set_individual(self, team, robot, individual):
        """set_individual <blue|yellow> robot individual"""
        if individual in _individuals:
            self.individuals[team][robot] = _individuals[individual](_get_robot(self, team, robot))
            self.write('ok')
        else:
            self.write('individual {} does not exist'.format(individual), ok=False)

    def set_goto_param(self, param, value):
        """set_goto_param param value

        ## default parameter values

        # attraction coefificients
        attraction_factor = 6.0
        attraction_power = 2.3
        attraction_floor = 80.0

        # repulsion coefificients
        repulsion_factor = 8.0
        repulsion_power = 3.3
        repulsion_floor = 0.0

        # magnetic coefificients
        magnetic_factor = 9.0
        magnetic_power = 3.1
        magnetic_floor = 0.0

        # delta_speed coefificients
        delta_speed_factor = 2.0
        delta_speed_power = 1.4
        delta_speed_floor = 0.0

        # minimum distance to use on the equation
        # anything smaller is capped to this
        min_distance = 1e-5

        # ignore other forces if attraction
        # force is as least this high:
        min_force_to_ignore_others = 100000

        # control params
        g = 9.80665
        mi = 0.1
        exp_k = 6
        """
        if hasattr(goto.Goto, param):
            try:
                setattr(goto.Goto, param, float(value))
                #self.write('ok')
                self.write('new value is {}'.format(getattr(goto.Goto, param)))
            except ValueError:
                self.write('invalid value {}'.format(value), ok=False)
        else:
            self.write('invalid param {}'.format(param), ok=False)

    #def print_goto_params(self):

    def hello(self):
        """hello -> world, simplest test of connectivity"""
        self.write('world')

    def help(self, cmd=None):
        """help [command]"""
        if cmd is None:
            self.write(
                '\n'.join([
                    'usage: help [command]',
                    'available commands:',
                ] + self.cmd_dict.keys() + ['quit'])
            )
        else:
            if cmd == 'quit':
                self.write('quit: end the intel')
            elif cmd in self.cmd_dict:
                cmd_func = self.cmd_dict[cmd].im_func
                self.write('{0.func_name}: {0.func_doc}'.format(cmd_func).strip())
            else:
                self.write('command "{}" not recognized'.format(cmd), ok=False)


class CLI(Thread):

    def __init__(self):
        super(CLI, self).__init__()
        self.debug = config['cli']['debug']
        self.quit = False
        self.world = World()

        # initial interface:
        default_interface = config['interface']['default']
        if default_interface == 'sim':
            self.interface = SimulationInterface(self.world)
        elif default_interface == 'tx':
            self.interface = TxInterface(self.world)
        else:
            #TODO: proper exception
            raise RuntimeError('interface {} not recognized'.format(default_interface))

        # Magic (grab attrs that do not begin with _)
        commands = filter(lambda i: not i.startswith('_'), dir(_commands))
        self.cmd_dict = {i: getattr(_commands, i) for i in commands}

        self.available_individuals = lambda robot: OrderedDict([
        ])

        self.available_plays = lambda team: OrderedDict([
        ])

        self.id_mapping = {"blue": {}, "yellow": {}}
        self.kick_mapping = {"blue": defaultdict(lambda: 100), "yellow": defaultdict(lambda: 100)}

        max_robots = 12
        self.plays = {"yellow": Dummy(), "blue": Dummy()}
        self.individuals = {"blue": {i: Dummy() for i in range(max_robots)}, "yellow": {i: Dummy() for i in range(max_robots)}}


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
        for p in self.plays.itervalues():
            p.step()
        for t in self.individuals.itervalues():
            for i in t.itervalues():
                i.step()

    def run(self):
        """
        Here lies the non-blocking code that will run on a different thread.
        The main purpose is to wait for input and iterpretate the given commands without blocking the main loop.
        """

        # wait a bit to make sure sockets are listening
        sleep(1)
        self.write("hello, intel is up!")

        while True:
            _cmd = self.read()
            cmd, args = _cmd['cmd'], _cmd['args']

            if cmd == 'q' or cmd == 'quit' or cmd == 'exit':
                # quit is special because it breaks the loop
                self.quit = True
                self.write('bye...')
                break
            else:
                if cmd in self.cmd_dict:
                    cmd_func = self.cmd_dict[cmd].im_func
                    try:
                        cmd_func(self, *args)
                    except TypeError as e:
                        self.write('{}: {}'.format(e.__class__.__name__, e), ok=False)
                        self.write('{0.func_name}: {0.func_doc}'.format(cmd_func), ok=False)
                    except Exception as e:
                        self.write('{}: {}'.format(e.__class__.__name__, e), ok=False)
                else:
                    self.write('command "{}" not recognized'.format(cmd), ok=False)

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
