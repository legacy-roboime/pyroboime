#
# Copyright (C) 2013-2015 RoboIME
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
from google.protobuf.message import DecodeError

from .network.multicast import MulticastReceiver
from .protos.messages_robocup_ssl_wrapper_pb2 import SSL_WrapperPacket as Wrapper


class VisionReceiver(MulticastReceiver):
    """
    Use this class to receive wrapper packets.

    Usage is very simple but it's likely to change because
    it clogs the execution until a packet is received.

    >>> receiver = VisionReceiver(('224.5.23.2', 10002))
    >>> packet = receiver.get_packet()
    """

    def __init__(self, address, intf):
        MulticastReceiver.__init__(self, address, intf)

    def get_packet(self):
        wrapper = Wrapper()
        try:
            wrapper.ParseFromString(self.recv())
        except DecodeError:
            pass
        return wrapper
