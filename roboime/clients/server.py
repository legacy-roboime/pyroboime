import zmq
import json

from .cli import CLI


class Server(CLI):
    def __init__(self):
        super(Server, self).__init__()
        self.ctx = zmq.Context()
        self.pub_port = 66655
        self.sub_port = 66654
        self.publisher = self.ctx.socket(zmq.PUSH)
        self.subscriber = self.ctx.socket(zmq.PULL)
        self.publisher.bind("tcp://*:{0}".format(self.pub_port))
        self.subscriber.connect("tcp://localhost:{0}".format(self.sub_port))
        print 'Listening on tcp://localhost:{0}'.format(self.sub_port)
        print 'Publishing on tcp://0.0.0.0:{0}'.format(self.pub_port)
        self.debug = True

    def read(self):
        string = self.subscriber.recv()
        if self.debug: 
            print string
        json_data = json.loads(string)
        if self.debug: print json_data
        return json_data

    def write(self, text):
        if self.debug: print text
        self.publisher.send(text)
