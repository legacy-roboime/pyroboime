from .multicast import MulticastReceiver
from .protos.messages_robocup_ssl_wrapper_pb2 import SSL_WrapperPacket

DEFAULT_ADDRESS = ('224.5.23.2', 10002)


class VisionReceiver(MulticastReceiver):

    def __init__(self, address=DEFAULT_ADDRESS):
        MulticastReceiver.__init__(self, address)

    def get_packet(self):
        wrapper_packet = SSL_WrapperPacket()
        wrapper_packet.ParseFromString(self.recv())
        return wrapper_packet

