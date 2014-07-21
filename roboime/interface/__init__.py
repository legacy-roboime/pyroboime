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
import sys
import struct
from multiprocessing import Process, Event
from . import updater
from . import commander
from . import filter
from ..config import config
from ..utils.profile import Profile
from ..utils import to_short
from ..utils.keydefaultdict import keydefaultdict


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

def send_update(commander, world, team):
        updates_dict = keydefaultdict(lambda x: '\x7f\x00\x00\x00\x00\x00\x00')

        for r in team:
            robot_packet = struct.pack('<bhhh', commander.mapping_dict[r.uid], to_short(1000 * r.x), to_short(1000 * r.y), to_short(100 * r.angle))
            #print (r.x, r.y, r.angle)
            updates_dict[commander.mapping_dict[r.uid]] = robot_packet

        # header [254, 0, 99]
        packet = '\xfe\x00\x63'
        for i in xrange(6):
            packet += updates_dict[i]
        # tail [55]
        packet += '\x37'

        #if self.debug:
        #    self.log(' '.join(map(lambda i: '{:02x}'.format(i), map(ord, packet))))

        commander.sender.send(packet, queue='field')


class Interface(Process, Profile):
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
        self.control_active_only = config['interface']['control_active_only']
        #self.updates = []
        #self.commands = []
        self.world = world
        self.updaters = updaters
        self.commanders = commanders
        self.filters = filters
        self.callback = callback
        self._exit = Event()

        # XXX: ugly but what the heck
        if not hasattr(self, 'blue_commander'):
            self.blue_commander = None
        if not hasattr(self, 'yellow_commander'):
            self.yellow_commander = None

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
        self.profile_reset()
        self.profile_stamp()

        has_update = False

        for up in self.updaters:
            if not up.queue.empty():
                #uu = up.queue.get_nowait()
                for _ in xrange(15):
                    uu = up.queue.get()
                    if up.queue.empty():
                        break
                for fi in reversed(self.filters):
                    _uu = fi.filter_update(uu)
                    if _uu is not None:
                        uu = _uu
                uu.apply(self.world)
                has_update = True

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

        # update the robots with their positions
        if has_update:
            if self.blue_commander is not None:
                send_update(self.blue_commander, self.world, self.world.blue_team)

            if self.yellow_commander is not None:
                send_update(self.yellow_commander, self.world, self.world.yellow_team)

        # actions extraction phase
        # TODO filtering
        self.profile_stamp()
        for co in self.commanders:
            actions = []
            # this is used to switch between control all and control active
            if self.control_active_only:
                r_iter = co.team
            else:
                r_iter = co.team.iterrobots(active=None)
            for r in r_iter:
                if r.action is not None:
                    actions.append(r.action)
            for fi in self.filters:
                _actions = fi.filter_command(actions)
                if _actions is not None:
                    actions = _actions

            #co.queue.put(actions)
            co.send(actions)

        self.profile_stamp()

    def processes(self):
        for up in self.updaters:
            yield up
        #for co in self.commanders:
        #    yield co


class TxInterface(Interface):

    def __init__(self, world, filters=[], command_blue=config['interface']['command-blue'], command_yellow=config['interface']['command-yellow'], mapping_yellow=None, mapping_blue=None, kick_mapping_yellow=None, kick_mapping_blue=None, **kwargs):
        debug = config['interface']['debug']
        vision_address = (config['interface']['tx']['vision-addr'], config['interface']['tx']['vision-port'])
        referee_address = (config['interface']['tx']['referee-addr'], config['interface']['tx']['referee-port'])
        commanders = []
        self.blue_commander = None
        self.yellow_commander = None
        if config['interface']['txver'] == 2012:
            ipaddr = config['interface']['oldtx_addr']
            port = config['interface']['oldtx_port']
            if command_blue:
                commanders.append(commander.Tx2012Commander(world.blue_team, mapping_dict=mapping_blue, kicking_power_dict=kick_mapping_blue, ipaddr=ipaddr, port=port))
            if command_yellow:
                commanders.append(commander.Tx2012Commander(world.yellow_team, mapping_dict=mapping_yellow, kicking_power_dict=kick_mapping_yellow, ipaddr=ipaddr, port=port))
        elif config['interface']['txver'] == 2013:
            if command_blue:
                commanders.append(commander.Tx2013Commander(world.blue_team, mapping_dict=mapping_blue, kicking_power_dict=kick_mapping_blue))
            if command_yellow:
                commanders.append(commander.Tx2013Commander(world.yellow_team, mapping_dict=mapping_yellow, kicking_power_dict=kick_mapping_yellow))
        else: # 2014, current
            if command_blue:
                self.blue_commander = commander.Tx2014Commander(world.blue_team, mapping_dict=mapping_blue, kicking_power_dict=kick_mapping_blue)
                commanders.append(self.blue_commander)
            if command_yellow:
                self.yellow_commander = commander.Tx2014Commander(world.yellow_team, mapping_dict=mapping_yellow, kicking_power_dict=kick_mapping_yellow)
                commanders.append(self.yellow_commander)
        super(TxInterface, self).__init__(
            world,
            updaters=[
                updater.VisionUpdater(vision_address),
                updater.RefereeUpdater(referee_address),
            ],
            commanders=commanders,
            filters=filters + [
                filter.KickoffFixExtended(camera_order=[3,1,2,0]),
                #filter.KickoffFix(),
                filter.DeactivateInactives(),
                # TESTIING
                #filter.LowPass(),
                #filter.Overlap(),
                #filter.MovingAverage(),
                filter.Acceleration(),
                filter.Speed(), # second speed is more precise due to Kalman, size=2
                #filter.CommandUpdateLog(options.cmdupd_filename),
                filter.Kalman(),
                filter.Speed(3), # first speed used to predict speed for Kalman
                #Noise should be enabled during simulation, to allow real noise simulation
                filter.RegisterPosition("input"),
                filter.Scale(),
            ],
            **kwargs
        )


class SimulationInterface(Interface):

    def __init__(self, world, filters=[], **kwargs):
        #debug = config['interface']['debug']
        vision_address = (config['interface']['sim']['vision-addr'], config['interface']['sim']['vision-port'])
        referee_address = (config['interface']['sim']['referee-addr'], config['interface']['sim']['referee-port'])
        grsim_address = (config['interface']['sim']['grsim-addr'], config['interface']['sim']['grsim-port'])
        super(SimulationInterface, self).__init__(
            world,
            updaters=[
                updater.VisionUpdater(vision_address),
                updater.RefereeUpdater(referee_address),
            ],
            commanders=[
                commander.SimCommander(world.blue_team, grsim_address),
                commander.SimCommander(world.yellow_team, grsim_address),
            ],
            filters=filters + [
                #filter.PositionLog(options.position_log_filename), #should be last, to have all data available
                #filter.LowPass(),
                filter.DeactivateInactives(),
                filter.Acceleration(),
                filter.Speed(), # second speed is more precise due to Kalman, size=2
                #filter.CommandUpdateLog(options.cmdupd_filename),
                filter.Kalman(),
                filter.Speed(3), # first speed used to predict speed for Kalman
                #Noise should be enabled during simulation, to allow real noise simulation
                #filter.Noise(options.noise_var_x,options.noise_var_y,options.noise_var_angle),
                filter.RegisterPosition("input"),
                filter.Scale(),
            ],
            **kwargs
        )

    #def start()
