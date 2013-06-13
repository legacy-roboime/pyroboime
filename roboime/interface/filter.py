from numpy import array
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
            #FIXME: This is motherfucking ugly and unpythonic. We certainly don't need to have hard-coded uids all over the filters.
            if u.uid() < 0x400 or u.uid() == 0xba11:
                self.previous[u.uid()] = u

    def filter_updates(self, updates):
        for u in updates:
            if u.uid() in self.previous:
                pu = self.previous[u.uid()]
                px, py, pt, = pu.data['x'], pu.data['y'], pu.data['timestamp']
                x, y, t = u.data['x'], u.data['y'], u.data['timestamp']
                u.data['speed'] = array((x - px, y - py)) / (t - pt)
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
        self.coef = [3., 0., -1. / 3., 0.]
        self.ux = defaultdict(local_factory=lambda: [0., 0., 0., 0.])
        self.uy = defaultdict(local_factory=lambda: [0., 0., 0., 0.])
        self.vx = defaultdict(local_factory=lambda: [0., 0., 0., 0.])
        self.vy = defaultdict(local_factory=lambda: [0., 0., 0., 0.])
        self.u0 = defaultdict(local_factory=lambda: [0., 0., 0., 0.])
        self.v0 = defaultdict(local_factory=lambda: [0., 0., 0., 0.])

def filter_updates(self, updates):
    for u in updates:
        if isinstance(update, RobotUpdate) or isinstance(update, BallUpdate):
            ux = self.ux[u.uid()]
            uy = self.uy[u.uid()]
            vx = self.vx[u.uid()]
            vy = self.vy[u.uid()]
            u0 = self.u0[u.uid()]
            v0 = self.v0[u.uid()]
    
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

            u.data['x'], u.data['y'] = vx[3], vy[3]

        # TODO: Angle filtering.
        if isinstance(update, RobotUpdate):
            pass
