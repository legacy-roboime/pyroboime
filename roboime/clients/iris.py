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
import IPython
from .cli import CLI


class IRIS(CLI):

    def __init__(self):
        super(IRIS, self).__init__()
        globals()['world'] = self.world
        for cmd, func in self.cmd_dict.iteritems():
            # XXX: creating a closure to avoid sharing references
            def _closure_hack():
                cmd_func = func.im_func
                global_func = lambda *args: cmd_func(self, *args)
                global_func.orig_func = cmd_func
                global_func.func_name = cmd_func.func_name
                global_func.func_doc = cmd_func.func_doc
                globals()[cmd] = global_func
            _closure_hack()

    def cli_loop(self):
        print 'Welcome to IRIS (Interactive RoboIME\'s Intelligence Shell)'
        #IPython.start_ipython()
        IPython.embed()
        # quit after ipython exits
        self.quit = True

    def write(self, text, ok=True):
        print text
