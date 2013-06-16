#if platform == 'win32':
#    from multiprocessing.dummy import Process, Queue, Event, Lock
#else:
#    from multiprocessing import Process, Queue, Event, Lock
from multiprocessing import Process, Queue, Event, Lock
from numpy import array

from ..communication import sslvision
from ..communication import sslrefbox
from .. import base


STOP_TIMEOUT = 1


class Update(object):

    def __init__(self, data):
        self.data = data

    def apply(self):
        raise NotImplemented


class BallUpdate(Update):

    def apply(self, world):
        ball = world.ball
        #for prop, value in self.data.iteritems():
        #    if prop != 'x' and prop != 'y':
        #        setattr(ball, prop, value)
        ball.update((self.data['x'], self.data['y']))
        if 'speed' in self.data:
            ball.speed = array(self.data['speed'])

    def uid(self):
        return 0xba11


class RobotUpdate(Update):

    def __init__(self, team_color, i, data):
        Update.__init__(self, data)
        self.team_color = team_color
        self.i = i

    def uid(self):
        if self.team_color == base.Blue:
            return 0x100 + self.i
        elif self.team_color == base.Yellow:
            return 0x200 + self.i
        else:
            raise Exception('Wrong color "{}"'.format(self.team_color))

    def apply(self, world):

        if self.team_color == base.Blue:
            team = world.blue_team
        elif self.team_color == base.Yellow:
            team = world.yellow_team
        robot = team[self.i]
        robot.active = True

        if robot.has_touched_ball:
            for r in robot.team:
                r.is_last_toucher = False
                r.has_touched_ball = False
            robot.is_last_toucher = True
            robot.has_touched_ball = False

        for prop, value in self.data.iteritems():
            if prop != 'x' and prop != 'y':
                setattr(robot, prop, value)
        robot.update((self.data['x'], self.data['y']))


class GeometryUpdate(Update):

    def apply(self, world):
        for prop, value in self.data.iteritems():
            setattr(world, prop, value)
        world.right_goal.update((world.length / 2, 0.0))
        world.left_goal.update((-world.length / 2, 0.0))
        world.inited = True

    def uid(self):
        return 0x6e0


class RefereeUpdate(Update):

    def apply(self, world):
        for prop, value in self.data.iteritems():
            setattr(world.referee, prop, value)

    def uid(self):
        return 0x43f3433


class TeamUpdate(Update):

    def __init__(self, team_color, data):
        super(TeamUpdate, self).__init__(data)
        self.team_color = team_color

    def apply(self, world):
        team = world.team(self.team_color)
        for prop, value in self.data.iteritems():
            setattr(team, prop, value)

    def uid(self):
        return 0x7e488


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
        raise NotImplemented


class VisionUpdater(Updater):

    def __init__(self, address):
        super(VisionUpdater, self).__init__()
        self.address = address

    def run(self):
        self.receiver = sslvision.VisionReceiver(self.address)
        super(VisionUpdater, self).run()

    def receive(self):
        updates = []
        packet = self.receiver.get_packet()

        if packet.HasField('geometry'):
            f = packet.geometry.field
            updates.append(GeometryUpdate({
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
            }))

        if packet.HasField('detection'):

            timestamp = packet.detection.t_capture

            for b in packet.detection.balls:
                updates.append(BallUpdate({
                    'timestamp': timestamp,
                    'x': b.x,
                    'y': b.y,
                }))

            for r in packet.detection.robots_yellow:
                updates.append(RobotUpdate(base.Yellow, r.robot_id, {
                    'timestamp': timestamp,
                    'x': r.x,
                    'y': r.y,
                    'angle': r.orientation,
                }))

            for r in packet.detection.robots_blue:
                updates.append(RobotUpdate(base.Blue, r.robot_id, {
                    'timestamp': timestamp,
                    'x': r.x,
                    'y': r.y,
                    'angle': r.orientation,
                }))

        return updates


class RealVisionUpdater(VisionUpdater):

    def __init__(self):
        VisionUpdater.__init__(self, ('224.5.23.2', 10002))


class SimVisionUpdater(VisionUpdater):

    def __init__(self):
        VisionUpdater.__init__(self, ('224.5.23.2', 11002))


class RefereeUpdater(Updater):

    def __init__(self):
        super(RefereeUpdater, self).__init__()
        #self.address = address
        self.counter = 0

    def run(self):
        #self.receiver = sslrefbox.SimRefboxReceiver(self.address)
        self.receiver = sslrefbox.SimRefboxReceiver()
        super(RefereeUpdater, self).run()

    def receive(self):
        updates = []
        referee = self.receiver.get_packet()
        updates.append(RefereeUpdate({
            'command': referee.command,
            'command_timestamp': referee.command_timestamp,
            'stage': referee.stage,
            'stage_time_left': referee.stage_time_left,
            'timestamp': referee.packet_timestamp,
        }))
        updates.append(TeamUpdate(base.Blue, {
            'score': referee.blue.score,
            'red_cards': referee.blue.red_cards,
            #'yellow_card_times': referee.blue.yellow_card_times,
            'yellow_cards': referee.blue.yellow_cards,
            'timeouts': referee.blue.timeouts,
            'timeout_time': referee.blue.timeout_time,
            'goalie': referee.blue.goalie,
        }))
        updates.append(TeamUpdate(base.Yellow, {
            'score': referee.yellow.score,
            'red_cards': referee.yellow.red_cards,
            #'yellow_card_times': referee.yellow.yellow_card_times,
            'yellow_cards': referee.yellow.yellow_cards,
            'timeouts': referee.yellow.timeouts,
            'timeout_time': referee.yellow.timeout_time,
            'goalie': referee.yellow.goalie,
        }))
        return updates
