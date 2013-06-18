from numpy import array
from numpy.random import normal
from math import degrees, sqrt
from roboime.interface.updater import RobotUpdate, BallUpdate, GeometryUpdate


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
        if self.file != None:
            for u in updates:
                self.file.write(str(u)+"\n")


class CommandUpdateLog(UpdateLog):
    """
    This filter is based on the UpdateLog filter and also stores commands.
    """
    def filter_commands(self, commands):
        if self.file != None:
            for c in commands:
                self.file.write("Cmd:" + str(c)+"\n")
                

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
            self.file = open(filename, 'w') #TODO: change to 'a' if want to append logs
            self.file.write("#Time\tUID\tx\ty\tangle" +
                            "\tinput_x\tinput_y\tinput_angle" +
                            "\tnoise_x\tnoise_y\tnoise_angle" +
                            "\n")
        except:
            self.file = None
            if filename != None:
                print("Could not open log file (%s). Continuing..." % (filename))
        super(PositionLog, self).__init__()
        
    def filter_updates(self, updates):
        if self.file != None:
            for u in updates:
                if u.uid() < 0x400 or u.uid() == 0xba11:
                    self.file.write("\n%f\t%s\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%f" % 
                     (u.data['timestamp'],
                      u.uid(),
                      u.data.get('x',0),
                      u.data.get('y',0),
                      u.data.get('angle',0),
                      u.data.get('input_x',0),
                      u.data.get('input_y',0),
                      u.data.get('input_angle',0),
                      u.data.get('noise_x',0),
                      u.data.get('noise_y',0),
                      u.data.get('noise_angle',0),
                     ))
                                                              

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
                u.data['input_x'] = u.data['x']
                u.data['input_y'] = u.data['y']
                u.data['x'] = normal(u.data['x'], self.std_dev_x)
                u.data['y'] = normal(u.data['y'], self.std_dev_y)
                u.data['noise_x'] = u.data['x']
                u.data['noise_y'] = u.data['y']
            if u.uid() < 0x400:
                u.data['input_angle'] = u.data['angle']
                u.data['angle'] = normal(u.data['angle'], self.std_dev_a)
                u.data['noise_angle'] = u.data['angle']
            
