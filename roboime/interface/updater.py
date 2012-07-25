from ..communication import sslvision


def _linear_scale(value):
    return value / 1000.0


def _angular_scale(value):
    return value


class Updater(object):

    field = None


class VisionUpdater(Updater):

    def __init__(self, field, address):
        self.field = field
        self.receiver = sslvision.VisionReceiver()

    def step(self):
        #TODO: create update objects instead of applying updates directely
        packet = self.receiver.get_packet()

        if packet.HasField('geometry'):
            f = packet.geometry.field
            self.field.width = _linear_scale(f.field_width)
            self.field.length = _linear_scale(f.field_length)
            self.field.line_width = _linear_scale(f.line_width)
            self.field.boundary_width = _linear_scale(f.boundary_width)
            self.field.referee_width = _linear_scale(f.referee_width)
            self.field.center_radius = _linear_scale(f.center_circle_radius)
            self.field.defense_radius = _linear_scale(f.defense_radius)
            self.field.defense_stretch = _linear_scale(f.defense_stretch)
            self.field.free_kick_distance = _linear_scale(f.free_kick_from_defense_dist)
            self.field.penalty_spot_distance = _linear_scale(f.penalty_spot_from_field_line_dist)
            self.field.penalty_line_distance = _linear_scale(f.penalty_line_from_spot_dist)
            self.field.goal_width = _linear_scale(f.goal_width)
            self.field.goal_depth = _linear_scale(f.goal_depth)
            self.field.goal_wall_width = _linear_scale(f.goal_wall_width)


        if packet.HasField('detection'):

            for b in packet.detection.balls:
                self.field.ball.x = _linear_scale(b.x)
                self.field.ball.y = _linear_scale(b.y)

            for r in packet.detection.robots_yellow:
                i = r.robot_id
                self.field.yellow_team[i].x = _linear_scale(r.x)
                self.field.yellow_team[i].y = _linear_scale(r.y)
                self.field.yellow_team[i].angle = _angular_scale(r.orientation)

            for r in packet.detection.robots_blue:
                i = r.robot_id
                self.field.blue_team[i].x = _linear_scale(r.x)
                self.field.blue_team[i].y = _linear_scale(r.y)
                self.field.blue_team[i].angle = _angular_scale(r.orientation)


class RealVisionUpdater(VisionUpdater):

    def __init__(self, field):
        self.field = field
        self.receiver = sslvision.RealVisionReceiver()


class SimVisionUpdater(VisionUpdater):

    def __init__(self, field):
        self.field = field
        self.receiver = sslvision.SimVisionReceiver()

