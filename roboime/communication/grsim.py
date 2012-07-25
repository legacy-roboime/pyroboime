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

