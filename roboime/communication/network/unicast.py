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
import socket


class Unicast(object):

    def __init__(self, address):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = address

    def close(self):
        self._sock.close()

    @property
    def host(self):
        return self.address[0]

    @host.setter
    def host(self, value):
        self.address = (value, self.port)

    @property
    def port(self):
        return self.address[1]

    @port.setter
    def port(self, value):
        self.address = (self.host, value)


class UnicastSender(Unicast):

    def send(self, data):
        self._sock.sendto(data, self.address)
