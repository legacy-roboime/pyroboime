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
from .cli import CLI


class Repl(CLI):

    def read(self):
        cmdlist = raw_input('> ').split() or ['']
        return {
            'cmd': cmdlist[0],
            'args': cmdlist[1:],
        }

    def write(self, text, ok=True):
        print text
