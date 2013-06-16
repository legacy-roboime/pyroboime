from numpy import array
from numpy import remainder
from math import degrees
from collections import defaultdict

from roboime.interface.updater import RobotUpdate, BallUpdate, GeometryUpdate


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
