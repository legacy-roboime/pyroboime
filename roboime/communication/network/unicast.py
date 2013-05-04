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
