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
from .. import Play
from ..tactics.goalkeeper import Goalkeeper
from ..tactics.striker import Striker
from ..tactics.mover import Mover
from ...config import config
from ...communication.protos.discrete_pb2 import Command


class Minimax(Play):
    """
    An externally computed play.
    """

    def __init__(self, team, **kwargs):
        """
        team: duh
        """
        super(Minimax, self).__init__(team, **kwargs)
        ctx = zmq.Context()
        self.socket = ctx.socket(zmq.REQ)
        self.socket.connect(config['minimax']['addr'])

        self.tactics_factory.update({
            'goalkeeper': lambda robot: Goalkeeper(robot, angle=0),
            'striker': lambda robot: Striker(robot),
            'mover': lambda robot: Mover(robot),
        })

    def step(self):
        # req reply:
        self.socket.send()
        cmd = Command.ParseFromString(self.socket.recv())

        for action in cmd.actions:
            pass
