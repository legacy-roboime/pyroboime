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
from ..tactics.passer import Passer
from ..tactics.mover import Mover
from ..tactics.waiter import Waiter
from ...config import config
from ...communication.protos.discrete_pb2 import Command
from ...communication.protos.discrete_pb2 import Action
from ...utils.geom import Point


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
            'passer': lambda robot: Passer(robot),
            'mover': lambda robot: Mover(robot),
            'wait': lambda robot: Waiter(robot),
        })

    def request(self, msg=''):
        self.socket.send(msg)
        c = Command()
        c.ParseFromString(self.socket.recv())
        return c

    def setup_tactics(self):
        cmd = self.request()

        for robot in self.team:
            r_id = robot.uid

            if r_id == self.goalie:
                robot.current_tactic = self.players[r_id]['goalkeeper']

            else:
                robot.current_tactic = self.players[r_id]['wait']

        for action in cmd.action:
            r_id = action.robot_id

            if r_id in self.team:
                robot = self.team[r_id]
                tactics = self.players[r_id]

                if action.type == Action.KICK:
                    tactic = tactics['striker']
                    tactic.lookpoint = Point(action.kick.x, action.kick.y)
                    robot.current_tactic = tactic

                elif action.type == Action.PASS:
                    tactic = tactics['passer']
                    tactic.lookpoint = self.team[getattr(action, 'pass').robot_id]
                    robot.current_tactic = tactic

                elif action.type == Action.MOVE:
                    tactic = tactics['mover']
                    tactic.target = Point(action.move.x, action.move.y)
                    robot.current_tactic = tactic
