#if platform == 'win32':
#    from multiprocessing.dummy import Process, Queue, Event, Lock
#else:
#    from multiprocessing import Process, Queue, Event, Lock
from multiprocessing import Process, Queue, Event, Lock
from numpy import array

from ..communication import sslvision
from ..communication import refbox
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
        return (0x100 if self.team_color is base.Blue else 0x200) + self.i

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
        # XXX: TEST
        world.referee_data = self.data


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

    def __init__(self, address=('224.5.23.1', 10001)):
        super(RefereeUpdater, self).__init__()
        self.receiver = refbox.RefboxOldReceiver(address)
        self.counter = 0

    def _command(self, char):
        """
        Command type     Command Description     Command
        =================================================================================
        Control commands
                         Halt                    H
                         Stop                    S
                         Ready                   ' ' (space character)
                         Start                   s
        Game Notifications
                         Begin first half        1
                         Begin half time         h
                         Begin second half       2
                         Begin overtime half 1   o
                         Begin overtime half 2   O
                         Begin penalty shootout  a

        Command type     Command Description     Yellow Team Command    Blue Team Command
        =================================================================================
        Game restarts
                         Kick off                k                      K
                         Penalty                 p                      P
                         Direct Free kick        f                      F
                         Indirect Free kick      i                      I
        Extras
                         Timeout                 t                      T
                         Timeout end             z                      z
                         Goal scored             g                      G
                         decrease Goal score     d                      D
                         Yellow Card             y                      Y
                         Red Card                r                      R
                         Cancel                  c
        """
        pass

    def receive(self):
        updates = []
        packet = self.receiver.get_packet()
        # receive until a command is issued
        try:
            while packet.counter < self.counter:
                packet = self.get_packet()
            self.counter = packet.counter
            updates.append(RefereeUpdate({
                'command': self._command(packet.command),
                'goals_blue': packet.goals_blue,
                'goals_yellow': packet.goals_yellow,
                'time_remaining': packet.time_remaining,
            }))
            return updates
        except:
            pass
