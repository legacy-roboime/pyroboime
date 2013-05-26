from numpy import array
from math import degrees


class Filter(object):
    """The filter class is the base for all filters.

    Filters should basically contain an filter_updates and
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
            if u.uid() < 0x400:
                self.previous[u.uid()] = u

    def filter_updates(self, updates):
        for u in updates:
            if u.uid() in self.previous:
                pu = self.previous[u.uid()]
                px, py, pt, = pu.data['x'], pu.data['y'], pu.data['timestamp']
                x, y, t = u.data['x'], u.data['y'], u.data['timestamp']
                u.data['speed'] = array((x - px, y - py)) / (t - pt)
        self.remember_updates(updates)
