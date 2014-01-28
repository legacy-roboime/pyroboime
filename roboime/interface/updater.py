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
from multiprocessing import Process, Queue, Event, Lock

from ..communication import sslvision
from ..communication import sslrefbox


STOP_TIMEOUT = 1


class Update(dict):

    def __init__(self, data):
        """
        >>> data = {
        ...     '__has_detection_data__': 1,
        ...     'blue_team': {
        ...         '__robots__': {
        ...             0: {'x': 2.0, 'y': 3.0},
        ...             3: {'x': -2.0, 'y': 4.0},
        ...             5: '__delete__',
        ...             4: {'x': 3.5, 'y': 0.5},
        ...         },
        ...         'goalie': 2,
        ...     },
        ...     'balls': [
        ...         {'x': -2.0, 'y': 5.0},
        ...         {'x': 4.0, 'y': -4.0},
        ...     ],
        ...     '__has_geometry_data__': 1,
        ...     'length': 6.0,
        ...     'width': 4.0,
        ...     '__has_referee_data__': 1,
        ...     'referee': {
        ...         'stage': 4,
        ...     },
        ... }
        """
        super(Update, self).__init__(data)

    def apply(self, world):
        for prop, value in self.iteritems():
            if prop in ('blue_team', 'yellow_team'):
                team = getattr(world, prop)

                # the expected format is to have a dict with uids mapping to dicts with
                # robot properties for each team, or instead of having
                for team_prop, team_value in value.iteritems():

                    # let's check if we have robot data
                    if team_prop == '__robots__':
                        for robot_id, robot_data in team_value.iteritems():
                            robot = team[robot_id]
                            #robot_data = team_value

                            # if instead of a dict the data is __delete__ it's used to signale
                            # that the robot is not seen anymore and should be deactivated
                            if robot_data == '__delete__':
                                robot.active = False

                            else:
                                robot.active = True
                                # x and y properties have a caveat, they cannot be set directly
                                # thus they must be set through the update method
                                robot.update(robot_data['x'], robot_data['y'])

                                # set all other properties the natuarl way
                                for prop, val in robot_data.iteritems():
                                    if prop not in ('x', 'y'):
                                        setattr(robot, prop, val)

                                #FIXME find the right place to do this:
                                if robot.has_touched_ball:
                                    for r in robot.team:
                                        r.is_last_toucher = False
                                        r.has_touched_ball = False
                                    robot.is_last_toucher = True
                                    robot.has_touched_ball = False


                    else:
                        setattr(team, team_prop, team_value)

            elif prop == 'referee':
                referee = world.referee

                # referee data is a dict, applied similary to the world
                for referee_prop, referee_prop_value in value.iteritems():
                    setattr(referee, referee_prop, referee_prop_value)

            elif prop == 'balls':
                #TODO somehow support for multiple balls
                if len(value) > 0:
                    ball_data = value[0]
                    world.ball.update(ball_data['x'], ball_data['y'])
                    for ball_prop, ball_prop_value in ball_data.iteritems():
                        if ball_prop not in ('x', 'y'):
                            setattr(world.ball, ball_prop, ball_prop_value)

            # ignore some metadata
            elif prop.startswith('__'):
                pass

            else:
                # all other properties go straight to the world
                setattr(world, prop, value)

        if self.has_geometry_data():
            world.right_goal.update((world.length / 2, 0.0))
            world.left_goal.update((-world.length / 2, 0.0))
            world.inited = True


    #def __str__(self):
    #    return "<{}: data={}>".format(type(self), super(Update, self))

    def has_detection_data(self):
        return '__detection_data__' in self

    def has_geometry_data(self):
        return '__geometry_data__' in self

    def has_referee_data(self):
        return '__referee_data__' in self

    def robots(self):
        for robot in self['blue_team']['__robots__'].iteritems():
            yield robot
        for robot in self['yellow_team']['__robots__'].iteritems():
            yield robot

    def balls(self):
        for ball_data in self['balls'].iteritems():
            yield ball_data

    def objects(self):
        for ball_data in self.balls():
            yield ball_data
        for robot_data in self.robots():
            yield robot_data

    def urobots(self):
        for uid, robot_data in self['blue_team']['__robots__'].iteritems():
            yield (('blue_team', uid), robot_data)
        for uid, robot_data in self['yellow_team']['__robots__'].iteritems():
            yield (('yellow_team', uid), robot_data)

    def uballs(self):
        for uid, ball_data in self['balls'].iteritems():
            yield (('balls', uid), ball_data)

    def uobjects(self):
        for uball in self.uballs():
            yield uball
        for urobot in self.urobots():
            yield urobot


class Updater(Process):

    def __init__(self, maxsize=15):
        Process.__init__(self)
        #self.queue = Queue(maxsize)
        self.queue = Queue()
        self.queue_lock = Lock()
        self._exit = Event()

    def run(self):
        while not self._exit.is_set():
            #with self.queue_lock:
            self.queue.put(self.receive())
            #self.queue.put_nowait(self.receive())
            #if self.queue.full():
            #    try:
            #        self.queue.get_nowait()
            #    except:
            #        pass

    def stop(self):
        self._exit.set()
        self.join(STOP_TIMEOUT)
        if self.is_alive():
            #TODO make a nicer warning
            print 'Terminating updater:', self
            self.terminate()

    def receive(self):
        raise NotImplementedError


class VisionUpdater(Updater):

    def __init__(self, address):
        super(VisionUpdater, self).__init__()
        self.address = address

    def run(self):
        self.receiver = sslvision.VisionReceiver(self.address)
        super(VisionUpdater, self).run()

    def receive(self):
        packet = self.receiver.get_packet()
        data = {}

        if packet.HasField('geometry'):
            f = packet.geometry.field
            data.update({
                '__geometry_data__': 1,
                'width': f.field_width,
                'length': f.field_length,
                'line_width': f.line_width,
                'boundary_width': f.boundary_width,
                'referee_width': f.referee_width,
                'center_radius': f.center_circle_radius,
                'defense_radius': f.defense_radius,
                'defense_stretch': f.defense_stretch,
                'free_kick_distance': f.free_kick_from_defense_dist,
                'penalty_spot_distance': f.penalty_spot_from_field_line_dist,
                'penalty_line_distance': f.penalty_line_from_spot_dist,
                'goal_width': f.goal_width,
                'goal_depth': f.goal_depth,
                'goal_wall_width': f.goal_wall_width,
            })

        if packet.HasField('detection'):
            data.update({
                'timestamp': packet.detection.t_capture,
                '__detection_data__': 1,
                'yellow_team': {'__robots__': {}},
                'blue_team': {'__robots__': {}},
                'balls': {},
            })

            balls = data['balls']
            for i, b in enumerate(packet.detection.balls):
                balls.update({i: {
                    'x': b.x,
                    'y': b.y,
                }})

            yellow_team = data['yellow_team']['__robots__']
            for r in packet.detection.robots_yellow:
                yellow_team.update({r.robot_id: {
                    'x': r.x,
                    'y': r.y,
                    'angle': r.orientation,
                }})

            blue_team = data['blue_team']['__robots__']
            for r in packet.detection.robots_blue:
                blue_team.update({r.robot_id: {
                    'x': r.x,
                    'y': r.y,
                    'angle': r.orientation,
                }})

        return Update(data)


class RefereeUpdater(Updater):

    def __init__(self, address):
        super(RefereeUpdater, self).__init__()
        self.address = address
        self.counter = 0

    def run(self):
        self.receiver = sslrefbox.RefboxReceiver(self.address)
        super(RefereeUpdater, self).run()

    def receive(self):
        referee = self.receiver.get_packet()

        data = {
            '__referee_data__': 1,
            'referee': {
                'command': referee.command,
                'command_timestamp': referee.command_timestamp,
                'stage': referee.stage,
                'stage_time_left': referee.stage_time_left,
                'timestamp': referee.packet_timestamp,
            },
            'blue_team': {
                'score': referee.blue.score,
                'red_cards': referee.blue.red_cards,
                #'yellow_card_times': referee.blue.yellow_card_times,
                'yellow_cards': referee.blue.yellow_cards,
                'timeouts': referee.blue.timeouts,
                'timeout_time': referee.blue.timeout_time,
                'goalie': referee.blue.goalie,
            },
            'yellow_team': {
                'score': referee.yellow.score,
                'red_cards': referee.yellow.red_cards,
                #'yellow_card_times': referee.yellow.yellow_card_times,
                'yellow_cards': referee.yellow.yellow_cards,
                'timeouts': referee.yellow.timeouts,
                'timeout_time': referee.yellow.timeout_time,
                'goalie': referee.yellow.goalie,
            }
        }

        return Update(data)
