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

    def __init__(self, address):
        MulticastReceiver.__init__(self, address)

    def get_packet(self):
        wrapper = Wrapper()
        try:
            wrapper.ParseFromString(self.recv())
        except DecodeError:
            pass
        return wrapper


class RealVisionReceiver(VisionReceiver):
    def __init__(self):
        VisionReceiver.__init__(self, ('224.5.23.2', 10002))


class SimVisionReceiver(VisionReceiver):
    def __init__(self):
        VisionReceiver.__init__(self, ('224.5.23.2', 11002))
