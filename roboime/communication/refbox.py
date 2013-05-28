from collections import namedtuple
from struct import unpack

from .network.multicast import MulticastReceiver


class RefboxOldReceiver(MulticastReceiver):
    """
    Use this class to receive chars from the old protocol.

    Usage is simple:

    >>> receiver = RefboxOldReceiver(('224.5.23.1', 10001))
    >>> packet = receiver.get_packet()
    """

    def __init__(self, address):
        super(RefboxOldReceiver, self).__init__(address)
        self._fmt = '!cBBBi'
        self.Packet = namedtuple('Packet', 'command counter goals_blue goals_yellow time_remaining')

    def get_packet(self):
        data = self.recv()
        try:
            return self.Packet(*unpack(self._fmt, data))
        except:
            print data
