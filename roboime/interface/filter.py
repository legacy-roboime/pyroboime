from numpy import array
from numpy import remainder
from numpy.random import normal
from math import degrees, sqrt
from collections import defaultdict

from roboime.interface.updater import RobotUpdate, BallUpdate, GeometryUpdate
from model import Model


class Filter(object):
    """The filter class is the base for all filters.

    Filters should basically contain filter_updates and
    filter_commands methods, those will be called with an
    iterator of updates and a list of commands respectively.

    Neither of those methods need to be implemented and
    if they return None the flow will continue.

    However if they return anything other than None it
    will replace the updates or commands for the next call.

    Please avoid returning lists, an iterator will generally
    have better perfomance and memory usage.
    """

    def filter_updates(self, updates):
        pass

    def filter_commands(self, commands):
        pass


class Scale(Filter):
    """
    This is a filter to correct scaling of values coming from
    and going to grSim. Ideally it should do arbitrary unit conversion
    but for now it doesn't.
    """

    def filter_updates(self, updates):
        for update in updates:
            if isinstance(update, RobotUpdate) or isinstance(update, BallUpdate) or isinstance(update, GeometryUpdate):
                filtered_data = {}
                for key, value in update.data.iteritems():
                    if key == 'timestamp':
                        filtered_data[key] = value
                    elif key == 'angle':
                        filtered_data[key] = degrees(value)
                    else:
                        filtered_data[key] = value / 1000.0
                update.data = filtered_data


class Speed(Filter):
    """
    This filter infers speed based on memorization of packages
    with smaller timestamps.

    The process per se is really stupid, speed = delta_space / delta_time,
    but in the lack of an smarter filter this should do fine.

    It seems a good idea to filter the data coming from this filter
    with something smarter.
    """

    def __init__(self):
        super(Speed, self).__init__()
        self.previous = {}

    def remember_updates(self, updates):
        for u in updates:
            if isinstance(u, RobotUpdate) or isinstance(u, BallUpdate):
                self.previous[u.uid()] = u

    def filter_updates(self, updates):
        for u in updates:
            if u.uid() in self.previous:
                pu = self.previous[u.uid()]
                px, py, pt, = pu.data['x'], pu.data['y'], pu.data['timestamp']
                x, y, t = u.data['x'], u.data['y'], u.data['timestamp']
                u.data['speed'] = array((x - px, y - py)) / (t - pt)
        self.remember_updates(updates)


class Acceleration(Filter):
    """
    This filter infers acceleration based on memorization of packages
    with smaller timestamps.

    The process per se is really stupid, accel = delta_speed / delta_time,
    but in the lack of an smarter filter this should do fine.

    It seems a good idea to filter the data coming from this filter
    with something smarter.
    """

    def __init__(self):
        super(Acceleration, self).__init__()
        self.previous = {}

    def remember_updates(self, updates):
        for u in updates:
            if (isinstance(u, RobotUpdate) or isinstance(u, BallUpdate)) and 'speed' in u.data:
                self.previous[u.uid()] = u

    def filter_updates(self, updates):
        for u in updates:
            if u.uid() in self.previous:
                pu = self.previous[u.uid()]
                ps, pt, = pu.data['speed'], pu.data['timestamp']
                s, t = u.data['speed'], u.data['timestamp']
                u.data['acceleration'] = (s - ps) / (t - pt)
        self.remember_updates(updates)


class LowPass(Filter):
    """
    This is a stub for a 4th order low-pass filter that eliminates high-frequency
    oscillations on positions..

    This filter's real purpose is to remove the oscillation in object positions which
    occurs when the fields of vision of two cameras overlap.
    """
    def __init__(self):
        super(LowPass, self).__init__()
        self.gain = 6.
        self.last_theta = None
        self.coef = [3., 0., -1. / 3., 0.]
        self.ux = defaultdict(lambda: [0., 0., 0., 0.])
        self.uy = defaultdict(lambda: [0., 0., 0., 0.])
        self.vx = defaultdict(lambda: [0., 0., 0., 0.])
        self.vy = defaultdict(lambda: [0., 0., 0., 0.])
        self.uo = defaultdict(lambda: [0., 0., 0., 0.])
        self.vo = defaultdict(lambda: [0., 0., 0., 0.])

    def filter_updates(self, updates):
        for u in updates:
            #print 'coe'
            if isinstance(u, RobotUpdate) or isinstance(u, BallUpdate):
                ux = self.ux[u.uid()]
                uy = self.uy[u.uid()]
                vx = self.vx[u.uid()]
                vy = self.vy[u.uid()]
                uo = self.uo[u.uid()]
                vo = self.vo[u.uid()]

                ux[0] = ux[1]
                ux[1] = ux[2]
                ux[2] = ux[3]
                ux[3] = u.data['x'] / self.gain
                vx[0] = vx[1]
                vx[1] = vx[2]
                vx[2] = vx[3]
                vx[3] = (ux[0] + ux[3]) + self.coef[0] * (ux[1] + ux[2]) + (self.coef[1] * vx[0]) + (self.coef[2] * vx[1]) + self.coef[3] * vx[2]

                uy[0] = uy[1]
                uy[1] = uy[2]
                uy[2] = uy[3]
                uy[3] = u.data['y'] / self.gain
                vy[0] = vy[1]
                vy[1] = vy[2]
                vy[2] = vy[3]
                vy[3] = (uy[0] + uy[3]) + self.coef[0] * (uy[1] + uy[2]) + (self.coef[1] * vy[0]) + (self.coef[2] * vy[1]) + self.coef[3] * vy[2]
                #print u.data['x'], vx[3]
                u.data['x'], u.data['y'] = vx[3], vy[3]

            # TODO: Angle filtering.
            if isinstance(u, RobotUpdate):
                theta = u.data['orientation']

                if self.last_theta is None:
                    self.last_theta = theta
                last_theta = self.last_theta

                d_theta = theta - last_theta
                d_theta = remainder(d_theta, 360)

                uo[0] = uo[1]
                uo[1] = uo[2]
                uo[2] = uo[3]
                uo[3] = d_theta / self.gain
                vo[0] = vo[1]
                vo[1] = vo[2]
                vo[2] = vo[3]
                vo[3] = (uo[0] + uo[3]) + self.coef[0] * (uo[1] + uo[2]) + (self.coef[1] * vo[0]) + (self.coef[2] * vo[1]) + self.coef[3] * vo[2]

                vo[3] = remainder(vo[3], 360)

                self.last_theta = theta + vo[3]
                u.data['orientation'] = vo[3] + theta


class UpdateLog(Filter):
    """
    This filter is a form of storing updates on a file for further debugging
    purposes.

    On instantiation, requires a filename to store updates. If the filename is
    None or if there is some problem opening the file, the filter just ignores
    the problem and goes on.
    """
    def __init__(self, filename):
        import datetime as dt
        try:
            self.file = open(filename, 'w')
            self.file.writelines(["Communications log file opened: %s\n" % (filename), "At %s\n" % (dt.datetime.now().isoformat(' '))])
        except:
            self.file = None
            print("Could not open log file (%s). Continuing..." % (filename))
        super(UpdateLog, self).__init__()

    def filter_updates(self, updates):
        if self.file is not None:
            for u in updates:
                self.file.write(str(u) + "\n")


class CommandUpdateLog(UpdateLog):
    """
    This filter is based on the UpdateLog filter and also stores commands.
    """
    def filter_commands(self, commands):
        if self.file is not None:
            for c in commands:
                self.file.write("Cmd:" + str(c) + "\n")


class PositionLog(Filter):
    """
    This filter stores the position data on a CSV file, with a format suitable
    for easy loading on a math program, like using pylab's loadtxt().

    The format is:
    timestamp   UID x   y   angle

    This format is stored as a header in the first line of the file, like a
    Python comment (start with #).
    """
    def __init__(self, filename):
        try:
            self.file = open(filename, 'w')  # TODO: change to 'a' if want to append logs
            self.file.write("#Time\tUID\tx\ty\tangle" +
                            "\tinput_x\tinput_y\tinput_angle" +
                            "\tnoise_x\tnoise_y\tnoise_angle" +
                            "\tspeed_vx\tspeed_vy\tspeed_vz" +
                            "\n")
        except:
            self.file = None
            if filename is not None:
                print("Could not open log file (%s). Continuing..." % (filename))
        super(PositionLog, self).__init__()

    def filter_updates(self, updates):
        if self.file is not None:
            for u in updates:
                if u.uid() < 0x400 or u.uid() == 0xba11:
                    vx, vy, w = u.data.get('speeds_cmd', (0,0,0))
                    self.file.write(("\n%f\t%s\t%f\t%f\t%f\t%f\t%f\t%f" +
                        "\t%f\t%f\t%f\t%f\t%f\t%f") % (
                        u.data['timestamp'],
                        u.uid(),
                        u.data.get('x', 0),
                        u.data.get('y', 0),
                        u.data.get('angle', 0),
                        u.data.get('input_x', 0),
                        u.data.get('input_y', 0),
                        u.data.get('input_angle', 0),
                        u.data.get('noise_x', 0),
                        u.data.get('noise_y', 0),
                        u.data.get('noise_angle', 0),
                        vx,
                        vy,
                        w,
                    ))


class RegisterPosition(Filter):
    """
    This filter registers the current position (x, y, angle) with new keys
    in the data dictionary.
    
    usage:
        RegisterPosition("prefix")
        #This will register new values for "prefix_x", "prefix_y" and
        # "prefix_angle" keys.
    """
    def __init__(self, prefix):
        self.prefix = prefix + "_"
        
    def filter_updates(self, updates):
        for u in updates:
            for suffix in ['x', 'y', 'angle']:
                if u.data.has_key(suffix):
                    u.data[self.prefix + suffix] = u.data[suffix]


class Noise(Filter):
    """
    This filter adds gaussian noise to the input x, y and angle variables. This
    is used to evaluate filter performance. Despite having this feature on
    grSim, using a filter inside the client allows storage of the data before
    the addition of noise. This allows easier performance comparison when
    PositionLog filters are added both before and after noise addition.

    Variances for x, y and angle data is defined on filter instantiation.
    """
    def __init__(self, variance_x, variance_y, variance_angle):
        # Standard deviation is the square root of the variance
        self.std_dev_x = sqrt(variance_x)
        self.std_dev_y = sqrt(variance_y)
        self.std_dev_a = sqrt(variance_angle)

    def filter_updates(self, updates):
        for u in updates:
            if u.uid() < 0x400 or u.uid() == 0xba11:
                u.data['x'] = normal(u.data['x'], self.std_dev_x)
                u.data['y'] = normal(u.data['y'], self.std_dev_y)
                u.data['noise_x'] = u.data['x']
                u.data['noise_y'] = u.data['y']
            if u.uid() < 0x400:
                u.data['angle'] = normal(u.data['angle'], self.std_dev_a)
                u.data['noise_angle'] = u.data['angle']


class Kalman(Filter):
    """
    This filter implements a Kalman Filter (KF) on the position measurements.

    The KF is applied independently on each measurement (x, y and angle), due
    to the complexity of modelling the whole robot (unfeasible in the current
    time schedule).
    """
    def __init__(self):
        self.models = {}

    def get_model(self, uid):
        model = self.models.get(uid, None)
        if model is None:
            model = Model(uid)
        self.models[uid] = model
        return model

    def filter_commands(self, commands):
        for c in commands:
            if c.uid < 0x400 or c.uid == 0xba11:
                self.get_model(c.uid).new_speed(c.absolute_speeds)

    def filter_updates(self, updates):
        for u in updates:
            if u.uid() < 0x400 or u.uid() == 0xba11:
                self.get_model(u.uid()).update(u.data)
