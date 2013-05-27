#!/usr/bin/env python -O
from sys import argv, exit
from PyQt4 import QtGui, QtCore

from roboime.clients import cute

if __name__ == '__main__':
    app = QtGui.QApplication(argv) 
    window = cute.Cute()
    exit(app.exec_())
else:
    raise Exception('This is not a module.')

