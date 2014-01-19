import zmq

from .cli import CLI


class Server(CLI):

    def __init__(self):
        super(Server, self).__init__()
        self.ctx = zmq.Context()

    def read(self):
        #TODO: implement using zmq
        return raw_input('> ')

    def write(self, text):
        #TODO: implement using zmq
        print text
