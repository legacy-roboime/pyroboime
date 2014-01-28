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
from .network.unicast import UnicastSender
from .protos.grSim_Packet_pb2 import grSim_Packet


class grSimSender(UnicastSender):

    def __init__(self, address=('127.0.0.1', 20011)):
        UnicastSender.__init__(self, address)

    def new_packet(self):
        return grSim_Packet()

    def send_packet(self, packet):
        data = packet.SerializeToString()
        self.send(data)
