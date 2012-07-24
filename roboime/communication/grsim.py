from .network.unicast import UnicastSender


class grSimSender(UnicastSender):

    def __init__(self, address=('127.0.0.1', 22011)):
        UnicastSender.__init__(self, address)

    def send_packet(packet):
        data = packet.SerializeToString()
        self.send(data)

