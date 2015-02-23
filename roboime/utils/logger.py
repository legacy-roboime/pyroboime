#
# Copyright (C) 2013-2015 RoboIME
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
