#!/usr/bin/env python
from sys import argv, exit
from multiprocessing import freeze_support

from roboime.clients.qtgraphical import App


def main():
    # try to debug with pudb, else pdb
    if '--debug' in argv:
        try:
            import pudb as pdb
        except ImportError:
            import pdb
        pdb.set_trace()

    app = App(argv)
    exit(app.exec_())


if __name__ == '__main__':
    freeze_support()
    main()

else:
    #raise Exception('This is not a module.')
    pass
