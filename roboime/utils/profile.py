from time import time


class Profile(object):

    def profile_reset(self):
        if hasattr(self, '_times'):
            self._deltas = map(lambda (t1, t2): 1e3 * (t2 - t1), zip(self._times[:-1], self._times[1:]))
        else:
            self._deltas = []
        self._times = []

    def profile_stamp(self):
        self._times.append(time())

    @property
    def profile_deltas(self):
        return self._deltas if hasattr(self, '_deltas') else []
