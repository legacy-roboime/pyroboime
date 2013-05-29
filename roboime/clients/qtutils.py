from PyQt4 import QtCore


class Lock(QtCore.QMutex):

    def __enter__(self):
        return self.lock()

    def __exit__(self, t, v, tb):
        self.unlock()
