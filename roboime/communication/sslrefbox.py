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
from collections import namedtuple
from struct import unpack

from .network.multicast import MulticastReceiver
from .protos.referee_pb2 import SSL_Referee


class RefboxReceiver(MulticastReceiver):
    """
    Use this class to receive refbox savestate packets.

    >>> receiver = RefboxReceiver(('224.5.23.1', 10003))
    >>> packet = receiver.get_packet()
    """

    def __init__(self, address):
        MulticastReceiver.__init__(self, address)

    def get_packet(self):
        referee = SSL_Referee()
        data = self.recv()
        #print data.encode('hex')
        referee.ParseFromString(data)
        return referee


#class RealRefboxReceiver(RefboxReceiver):
#    def __init__(self):
#        super(RealRefboxReceiver, self).__init__(('224.5.23.1', 10003))
#
#
#class SimRefboxReceiver(RefboxReceiver):
#    def __init__(self):
#        super(SimRefboxReceiver, self).__init__(('224.5.23.1', 11003))


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
