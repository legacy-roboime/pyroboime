#!/usr/bin/env python -O
from sys import argv, exit
from PyQt4 import QtGui

from roboime.clients import qtgraphical

if __name__ == '__main__':
    if '--debug' in argv:
        try:
            import pudb as pdb
        except ImportError:
            import pdb
        pdb.set_trace()
    app = QtGui.QApplication(argv)
    window = qtgraphical.QtGraphicalClient()
    exit(app.exec_())
else:
    raise Exception('This is not a module.')

