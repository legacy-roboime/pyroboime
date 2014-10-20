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
from ..config import config


class Log(object):
    def __init__(self, key):
        self._debug = config[key]['debug']
        if self._debug:
            self._log = True
            if config[key]['log-file'] == 'STDOUT':
                self._log_file = sys.stdout
            elif config[key]['log-file'] == 'STDERR':
                self._log_file = sys.stderr
            else:
                self._log_file = open(config[key]['log-file'], 'a')
        else:
            self._log = False
        pass

    def __call__(self, message):
        if self._log:
            self._log_file.write(str(message))
            self._log_file.write('\n')
            self._log_file.flush()

    def debug(self, message):
        if self._debug:
            self.__call__(message)
