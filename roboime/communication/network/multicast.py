import socket

MULTICAST_TTL = 20
MAX_BUFFER_SIZE = 1024


class Multicast(object):

    def __init__(self, address):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = address

    def close(self):
        self._sock.close()

    @property
    def group(self):
        return self.address[0]

    @group.setter
    def group(self, value):
        self.address = (value, self.port)

    @property
    def port(self):
        return self.address[1]

    @port.setter
    def port(self, value):
        self.address = (self.group, value)


class MulticastSender(Multicast):
    """Extension of socket for sending multicast messages."""

    def __init__(self, address):
        Multicast.__init__(self, address)

        # Make the socket multicast-aware, and set TTL.
        self._sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)

    def send(self, data):
        # Send the data
        self._sock.sendto(data, self.address)


class MulticastReceiver(Multicast):
    """Extension of socket for receiving multicast messages."""

    def __init__(self, address):
        Multicast.__init__(self, address)

        # Set some options to make it multicast-friendly
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
                self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except AttributeError:
                pass # Some systems don't support SO_REUSEPORT
        self._sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
        self._sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 1)

        # Bind to the port
        self._sock.bind(('', self.port))

        # Set some more multicast options
        intf = socket.gethostbyname(socket.gethostname())
        self._sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(intf) + socket.inet_aton('0.0.0.0'))
        self._sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(self.group) + socket.inet_aton('0.0.0.0'))

    def recv(self, buf_size=MAX_BUFFER_SIZE):
        # Receive the data, then unregister multicast receive membership, then close the port
        data, sender_addr = self._sock.recvfrom(buf_size)
        self._sock.setsockopt(socket.SOL_IP, socket.IP_DROP_MEMBERSHIP, socket.inet_aton(self.group) + socket.inet_aton('0.0.0.0'))
        return data

