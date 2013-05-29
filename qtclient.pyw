#!/usr/bin/env python
from sys import argv, exit

from roboime.clients.qtgraphical import App

if __name__ == '__main__':

    # try to debug with pudb, else pdb
    if '--debug' in argv:
        try:
            import pudb as pdb
        except ImportError:
            import pdb
        pdb.set_trace()

    app = App(argv)
    exit(app.exec_())

else:
    raise Exception('This is not a module.')
