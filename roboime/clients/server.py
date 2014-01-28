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
        self.write(' '.join([json_data['cmd']] + json_data['args'] or []), None)

        return json_data

    def write(self, text, ok=True):
        if self.debug:
            print 'out:', '"{}"'.format(text), 'ok:', ok

        self.publisher.send(json.dumps({
            'out': text,
            'ok': ok,
        }))
