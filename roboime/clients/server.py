#
# Copyright (C) 2013-2015 RoboIME
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

from .cli import CLI
from ..config import config


class Server(CLI):
    def __init__(self):
        super(Server, self).__init__()
        ctx = zmq.Context()

        self.publisher = ctx.socket(zmq.PUB)
        self.puller = ctx.socket(zmq.PULL)
        self.publisher.bind(config['zmq']['pub'])
        self.puller.bind(config['zmq']['pull'])
        print 'cli publishing to {}'.format(config['zmq']['pub'])
        print 'cli pulling on {}'.format(config['zmq']['pull'])

    def read(self):
        json_data = self.puller.recv_json()
        if self.debug:
            print json_data

        # confirm the command was received:
        self.write(' '.join([json_data['cmd']] + json_data['args'] or []), None)

        return json_data

    def write(self, text, ok=True):
        if self.debug:
            print 'out:', '"{}"'.format(text), 'ok:', ok

        self.publisher.send_json({
            'out': text,
            'ok': ok,
        })
