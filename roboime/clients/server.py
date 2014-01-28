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

    def read(self):
        string = self.subscriber.recv()
        json_data = json.loads(string)
        if self.debug:
            print json_data

        # confirm the command was received:
        self.write(' '.join([json_data['cmd']] + json_data['args'] or []))

        return json_data

    def write(self, text, ok=True):
        if self.debug:
            print 'out:', '"{}"'.format(text), 'ok:', ok

        self.publisher.send(json.dumps({
            'out': text,
            'ok': ok,
        }))
