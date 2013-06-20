class Logger(object):
    """
    This class is a generic logger interface.
    """
    def __init__(self, filename):
        import datetime as dt
        try:
            self.file = open(filename, 'w')
            self.file.writelines(["Communications log file opened: %s\n" % (filename), "At %s\n" % (dt.datetime.now().isoformat(' '))])
        except:
            self.file = None
            print("Could not open log file (%s). Continuing..." % (filename))

    def filter_updates(self, updates):
        if self.file is not None:
            for u in updates:
                self.file.write(str(u) + "\n")
