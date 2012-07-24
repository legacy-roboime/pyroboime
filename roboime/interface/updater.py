from ..communication import sslvision


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
            self.field.width = f.field_width
            self.field.length = f.field_length
            self.field.line_width = f.line_width
            self.field.boundary_width = f.boundary_width
            self.field.referee_width = f.referee_width
            self.field.center_radius = f.center_circle_radius
            self.field.defense_radius = f.defense_radius
            self.field.defense_stretch = f.defense_stretch
            self.field.free_kick_distance = f.free_kick_from_defense_dist
            self.field.penalty_spot_distance = f.penalty_spot_from_field_line_dist
            self.field.penalty_line_distance = f.penalty_line_from_spot_dist
            self.field.goal_width = f.goal_width
            self.field.goal_depth = f.goal_depth
            self.field.goal_wall_width = f.goal_wall_width


        if packet.HasField('detection'):

            for b in packet.detection.balls:
                self.field.ball.x = b.x
                self.field.ball.y = b.y

            for r in packet.detection.robots_yellow:
                #self.field.
                #TODO: finish this

