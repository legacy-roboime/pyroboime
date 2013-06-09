from collections import namedtuple
from struct import unpack

from .network.multicast import MulticastReceiver
from .protos.referee_pb2 import SSL_Referee
from .protos.savestate_pb2 import SaveState
from ..base import Referee

#CommandsDict = dict((k, v) for (v, k) in SSL_Referee.Command.items())
#StagesDict = dict((k, v) for (v, k) in SSL_Referee.Stage.items())
CommandsDict = dict((getattr(SSL_Referee, getattr(Referee.Command, name)), getattr(Referee.Command, name)) for name in dir(Referee.Command) if not name.startswith('_'))
StagesDict = dict((getattr(SSL_Referee, getattr(Referee.Stage, name)), getattr(Referee.Stage, name)) for name in dir(Referee.Stage) if not name.startswith('_'))


class RefboxReceiver(MulticastReceiver):
    """
    Use this class to receive refbox savestate packets.

    >>> receiver = RefboxReceiver(('224.5.23.1', 10003))
    >>> packet = receiver.get_packet()
    """

    def __init__(self, address):
        MulticastReceiver.__init__(self, address)

    def get_packet(self):
        state = SaveState()
        state.ParseFromString(self.recv())
        return state


class RealRefboxReceiver(RefboxReceiver):
    def __init__(self):
        super(RealRefboxReceiver, self).__init__(('224.5.23.1', 10003))


class SimRefboxReceiver(RefboxReceiver):
    def __init__(self):
        super(SimRefboxReceiver, self).__init__(('224.5.23.1', 11003))


class RefboxLegacyReceiver(MulticastReceiver):
    """
    Use this class to receive chars from the old protocol.

    Usage is simple:

    >>> receiver = RefboxLegacyReceiver(('224.5.23.1', 10001))
    >>> packet = receiver.get_packet()
    """

    def __init__(self, address):
        super(RefboxLegacyReceiver, self).__init__(address)
        self._fmt = '!cBBBi'
        self.Packet = namedtuple('Packet', 'command counter goals_blue goals_yellow time_remaining')

    def _commmand(self):
        """
        Command type     Command Description     Command
        =================================================================================
        Control commands
                         Halt                    H
                         Stop                    S
                         Ready                   ' ' (space character)
                         Start                   s
        Game Notifications
                         Begin first half        1
                         Begin half time         h
                         Begin second half       2
                         Begin overtime half 1   o
                         Begin overtime half 2   O
                         Begin penalty shootout  a

        Command type     Command Description     Yellow Team Command    Blue Team Command
        =================================================================================
        Game restarts
                         Kick off                k                      K
                         Penalty                 p                      P
                         Direct Free kick        f                      F
                         Indirect Free kick      i                      I
        Extras
                         Timeout                 t                      T
                         Timeout end             z                      z
                         Goal scored             g                      G
                         decrease Goal score     d                      D
                         Yellow Card             y                      Y
                         Red Card                r                      R
                         Cancel                  c
        """

    def get_packet(self):
        data = self.recv()
        try:
            return self.Packet(*unpack(self._fmt, data))
        except:
            print data
