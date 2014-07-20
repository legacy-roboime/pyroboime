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
from numpy import array
from numpy.random import normal
from math import degrees, sqrt
from collections import defaultdict

from model import Model


class Filter(object):
    """The filter class is the base for all filters.

    Filters should basically contain filter_update and
    filter_command methods, those will be called with an
    iterator of updates and a list of commands respectively.

    Neither of those methods need to be implemented and
    if they return None the flow will continue.

    However if they return anything other than None it
    will replace the updates or commands for the next call.

    Please avoid returning lists, an iterator will generally
    have better performance and memory usage.
    """

    def filter_update(self, updates):
        pass

    def filter_command(self, commands):
        pass


class Overlap(Filter):
    """
    Removes everything a camera removes beyond a certain x position.
    Designed to reduce camera overlap
    """
    def __init__(self):
        self.x_threshold = 0.0

    def filter_update(self, update):
        if update.has_detection_data():
            for uid, u in update['balls'].copy().iteritems():#.objects():
                if u['x'] > self.x_threshold and update['camera'] == 0:
                #if update['camera'] == 0:
                    del update['balls'][uid]
                if u['x'] < -self.x_threshold and update['camera'] == 1:
                    del update['balls'][uid]

            for uid, u in update['blue_team']['__robots__'].copy().iteritems():
                if u['x'] > self.x_threshold and update['camera'] == 0:
                #if update['camera'] == 0:
                    del update['blue_team']['__robots__'][uid]
                if u['x'] < -self.x_threshold and update['camera'] == 1:
                    del update['blue_team']['__robots__'][uid]

            for uid, u in update['yellow_team']['__robots__'].copy().iteritems():
                if u['x'] > self.x_threshold and update['camera'] == 0:
                #if update['camera'] == 0:
                    del update['yellow_team']['__robots__'][uid]
                if u['x'] < -self.x_threshold and update['camera'] == 1:
                    del update['yellow_team']['__robots__'][uid]

class IgnoreCamera(Filter):
    """
    Removes everything a camera removes beyond a certain x position.
    Designed to reduce camera overlap
    """
    def __init__(self, camId):
        self.x_threshold = 0.04
        self.camId = camId

    def filter_update(self, update):
        if update.has_detection_data():
            for uid, u in update['balls'].copy().iteritems():
                if update['camera'] == self.camId:
                    del update['balls'][uid]

            for uid, u in update['blue_team']['__robots__'].copy().iteritems():
                if update['camera'] == self.camId:
                    del update['blue_team']['__robots__'][uid]

            for uid, u in update['yellow_team']['__robots__'].copy().iteritems():
                if update['camera'] == self.camId:
                    del update['yellow_team']['__robots__'][uid]

class Scale(Filter):
    """
    This is a filter to correct scaling of values coming from
    and going to grSim. Ideally it should do arbitrary unit conversion
    but for now it doesn't.
    """

    geom_fields = [
        'width',
        'length',
        'line_width',
        'boundary_width',
        'referee_width',
        'center_radius',
        'defense_radius',
        'defense_stretch',
        'free_kick_distance',
        'penalty_spot_distance',
        'penalty_line_distance',
        'goal_width',
        'goal_depth',
        'goal_wall_width',
    ]

    def __init__(self, from_unit='mm', to_unit='m'):
        self.from_unit = from_unit
        self.to_unit = to_unit

    def filter_update(self, update):
        if update.get('__unit__', self.from_unit) == self.from_unit:
            update['__unit__'] = self.to_unit

            #TODO this should be calculated from the units
            ratio = 1e-3

            # convert robot positions
            if update.has_detection_data():
                for uid, u in update.objects():
                    if u is not '__delete__':
                        u['x'] *= ratio
                        u['y'] *= ratio
                        if 'angle' in u:
                            u['angle'] = degrees(u['angle'])

            if update.has_geometry_data():
                for key in self.geom_fields:
                    if key in update:
                        update[key] *= ratio


class Speed(Filter):
    """
    This filter infers speed based on memorization of packages
    with smaller timestamps.

    The process per se is really stupid, speed = delta_space / delta_time,
    but in the lack of an smarter filter this should do fine.

    It seems a good idea to filter the data coming from this filter
    with something smarter.
    """

    def __init__(self, size=2):
        super(Speed, self).__init__()
        self.previous = {'timestamp': 0}
        self.size = size
        #FIXME: size is a hack, because speeds should be 3-shaped
        # (x, y, w), where w is angular speed
        # since too many places use speeds as a 2-element array, I'm just
        # shrinking it at the end

    def remember_update(self, update):
        self.previous['timestamp'] = update['timestamp']
        for uid, u in update.uobjects():
            if u is not '__delete__':
                self.previous[uid] = u

    def filter_update(self, update):
        if update.has_detection_data():
            pt = self.previous['timestamp']
            t = update['timestamp']
            for uid, u in update.uobjects():
                if u is not '__delete__':
                    if uid in self.previous:
                        pu = self.previous[uid]
                        px, py, pa = pu['x'], pu['y'], pu.get('angle', 0.0)
                        x, y, a = u['x'], u['y'], u.get('angle', 0.0)
                        speed = array((x - px, y - py, a - pa)) / (t - pt)
                        u['speed'] = speed[:self.size]
                    else:
                        u['speed'] = array((0.0, 0.0, 0.0))[:self.size]
            self.remember_update(update)


class Acceleration(Filter):
    """
    This filter infers acceleration based on memorization of packages
    with smaller timestamps.

    The process per se is really stupid, accel = delta_speed / delta_time,
    but in the lack of an smarter filter this should do fine.

    It seems a good idea to filter the data coming from this filter
    with something smarter.
    """

    def __init__(self, size=2):
        super(Acceleration, self).__init__()
        self.previous = {'timestamp': 0}
        self.size = size
        #FIXME: size is a hack, because speeds should be 3-shaped
        # (x, y, w), where w is angular speed
        # since too many places use speeds as a 2-element array, I'm just
        # shrinking it at the end

    def remember_update(self, update):
        self.previous['timestamp'] = update['timestamp']
        for uid, u in update.uobjects():
            if u is not '__delete__':
                self.previous[uid] = u

    def filter_update(self, update):
        if update.has_detection_data():
            pt = self.previous['timestamp']
            t = update['timestamp']
            dt = t - pt
            for uid, u in update.uobjects():
                if u is not '__delete__':
                    if uid in self.previous:
                        pu = self.previous[uid]
                        ps = pu['speed']
                        s = u['speed']
                        # even though dt is not supposed to be 0 at any
                        # time it's sane to check
                        if dt != 0.0:
                            u['acceleration'] = (s - ps) / dt
                    else:
                        u['acceleration'] = array((0.0, 0.0, 0.0))[:self.size]
            self.remember_update(update)


class MovingAverage(Filter):
    """
    Averages the last 2 positions to get the current one. This is fucking stupid
    """
    def __init__(self):
        super(MovingAverage, self).__init__()
        self.lx = defaultdict(lambda: 0.0)
        self.ly = defaultdict(lambda: 0.0)
        self.lo = defaultdict(lambda: 0.0)

    def filter_update(self, update):
        if update.has_detection_data():
            for uid, u in update.uobjects():
                cx = self.lx[uid]
                cy = self.ly[uid]
                co = self.lo[uid]

                self.lx[uid], self.ly[uid] = u['x'], u['y']

                u['x'], u['y'] = (cx + self.lx[uid]) / 2, (cy + self.ly[uid]) / 2
                if 'angle' in u:
                    self.lo[uid] = u['angle']
                    while co > 180:
                        co -= 360
                    while co < -180:
                        co += 360
                    while self.lo[uid] > 180:
                        self.lo[uid] -= 360
                    while self.lo[uid] < -180:
                        self.lo[uid] += 360
                    u['angle'] = (co + self.lo[uid]) / 2


class LowPass(Filter):
    """
    This is a stub for a 4th order low-pass filter that eliminates high-frequency
    oscillations on positions..

    This filter's real purpose is to remove the oscillation in object positions which
    occurs when the fields of vision of two cameras overlap.
    """
    def __init__(self):
        super(LowPass, self).__init__()
        self.gain = 2.494054261
        self.last_theta = None
        self.coef = [3.0, -0.1314787742, -0.751697685, -1.3609801469]
        self.ux = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])
        self.uy = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])
        self.vx = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])
        self.vy = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])
        self.uo = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])
        self.vo = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])

    def filter_update(self, update):
        if update.has_detection_data():
            for uid, u in update.uobjects():
                ux = self.ux[uid]
                uy = self.uy[uid]
                vx = self.vx[uid]
                vy = self.vy[uid]
                uo = self.uo[uid]
                vo = self.vo[uid]

                ux[0] = ux[1]
                ux[1] = ux[2]
                ux[2] = ux[3]
                ux[3] = u['x'] / self.gain
                vx[0] = vx[1]
                vx[1] = vx[2]
                vx[2] = vx[3]
                vx[3] = (ux[0] + ux[3]) + self.coef[0] * (ux[1] + ux[2]) + (self.coef[1] * vx[0]) + (self.coef[2] * vx[1]) + self.coef[3] * vx[2]

                uy[0] = uy[1]
                uy[1] = uy[2]
                uy[2] = uy[3]
                uy[3] = u['y'] / self.gain
                vy[0] = vy[1]
                vy[1] = vy[2]
                vy[2] = vy[3]
                vy[3] = (uy[0] + uy[3]) + self.coef[0] * (uy[1] + uy[2]) + (self.coef[1] * vy[0]) + (self.coef[2] * vy[1]) + self.coef[3] * vy[2]
                u['x'], u['y'] = vx[3], vy[3]

                # TODO: Angle filtering.
                if 'angle' in u:
                    theta = u['angle']

                    if self.last_theta is None:
                        self.last_theta = theta
                    last_theta = self.last_theta

                    d_theta = theta - last_theta
                    while d_theta > 180:
                        d_theta -= 360
                    while d_theta < -180:
                        d_theta += 360

                    uo[0] = uo[1]
                    uo[1] = uo[2]
                    uo[2] = uo[3]
                    uo[3] = d_theta / self.gain
                    vo[0] = vo[1]
                    vo[1] = vo[2]
                    vo[2] = vo[3]
                    vo[3] = (uo[0] + uo[3]) + self.coef[0] * (uo[1] + uo[2]) + (self.coef[1] * vo[0]) + (self.coef[2] * vo[1]) + self.coef[3] * vo[2]

                    self.last_theta = theta + vo[3]
                    while self.last_theta > 180:
                        self.last_theta -= 360
                    while self.last_theta < -180:
                        self.last_theta += 360
                    #u['angle'] = self.last_theta


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

    def filter_update(self, updates):
        if self.file is not None:
            for u in updates:
                self.file.write(str(u) + "\n")


class CommandUpdateLog(UpdateLog):
    """
    This filter is based on the UpdateLog filter and also stores commands.
    """
    def filter_command(self, command):
        if self.file is not None:
            for a in command:
                self.file.write("Cmd:" + str(a) + "\n")


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
            # TODO: change to 'a' if want to append logs
            self.file = open(filename, 'w')
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

    def filter_update(self, update):
        if self.file is not None:
            if update.has_detection_data():
                for uid, object_data in update.objects():
                    self.file.write("\n%f\t%s\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%f" % (
                        object_data['timestamp'],
                        uid,
                        object_data.get('x', '-'),
                        object_data.get('y', '-'),
                        object_data.get('angle', '-'),
                        object_data.get('input_x', '-'),
                        object_data.get('input_y', '-'),
                        object_data.get('input_angle', '-'),
                        object_data.get('noise_x', '-'),
                        object_data.get('noise_y', '-'),
                        object_data.get('noise_angle', '-'),
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
                if suffix in u:
                    u[self.prefix + suffix] = u[suffix]


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

    def filter_update(self, update):
        if update.has_detection_data():
            for uid, object_data in update.objects():
                object_data['input_x'] = object_data['x']
                object_data['x'] = normal(object_data['x'], self.std_dev_x)
                object_data['noise_x'] = object_data['x']

                object_data['input_y'] = object_data['y']
                object_data['y'] = normal(object_data['y'], self.std_dev_y)
                object_data['noise_y'] = object_data['y']

                if uid != 'ball':
                    object_data['input_angle'] = object_data['angle']
                    object_data['angle'] = normal(object_data['angle'], self.std_dev_a)
                    object_data['noise_angle'] = object_data['angle']


class Kalman(Filter):
    """
    This filter implements a Kalman Filter (KF) on the position measurements.

    The KF is applied independently on each measurement (x, y and angle), due
    to the complexity of modelling the whole robot (unfeasible in the current
    time schedule).
    """
    def __init__(self):
        super(Kalman, self).__init__()
        self.models = {}

    def get_model(self, uid):
        model = self.models.get(uid, None)
        if model is None:
            model = Model(uid)
        self.models[uid] = model
        return model

    #def filter_command(self, commands):
    #    for c in commands:
    #        if c.uid < 0x400 or c.uid == 0xba11:
    #            self.get_model(c.uid).new_speed(c.absolute_speeds)

    def filter_update(self, update):
        if update.has_detection_data():
            for uid, object_data in update.objects():
                if 'speed' in object_data and 'acceleration' in object_data:
                    pass
                    #m = self.get_model(u.uid())
                    #m.update(u)
                    #m.new_speed(u['speed'])


class DeactivateInactives(Filter):
    """
    This filter will deactivate robots which are not seen after a given time.
    """

    def __init__(self, timeout=1.0):
        self.timeout = timeout
        self.previous = {}

    def remember_update(self, update):
        t = update['timestamp']
        for uid, u in update.uobjects():
            if u is not '__delete__':
                self.previous[uid] = t
            else:
                del self.previous[uid]

    def filter_update(self, update):
        if update.has_detection_data():
            t = update['timestamp']
            for (uid, pt) in self.previous.iteritems():
                path, i = uid
                d = update[path] if path == 'balls' else update[path]['__robots__']
                #t = d[i]
                if t - pt > self.timeout:
                    d[i] = '__delete__'
            self.remember_update(update)


#class IgnoreSide(Filter):
#
#    def __init__(self, side_to_ignore='+'):
#        self.side_to_ignore = side_to_ignore
#        super(IgnoreSide, self).__init__()
#
#    def filter_updates(self, updates):
#        sign = -1 if self.side_to_ignore == '-' else 1
#        to_be_removed = []
#        for u in updates:
#            if 'x' in u:
#                if u['x'] * sign > 0:
#                    to_be_removed.append(u)
#        for u in to_be_removed:
#            updates.remove(u)

class KickoffFix(Filter):
    """
    Removes everything a camera removes beyond a certain x position.
    Designed to reduce camera overlap
    """
    def __init__(self):
        self.x_threshold = 0.10 # TODO: Needs calibration
        self.old_cam = 0

    def filter_update(self, update):
        if update.has_detection_data():
            for uid, u in update['balls'].copy().iteritems():#.objects():
                if u['x'] < -self.x_threshold and update['camera'] == 0:
                    del update['balls'][uid]
                    self.old_cam = 1
                elif u['x'] > self.x_threshold and update['camera'] == 1:
                    del update['balls'][uid]
                    self.old_cam = 0
                elif u['x'] > -self.x_threshold and u['x'] < self.x_threshold and update['camera'] != self.old_cam:
                    del update['balls'][uid]
