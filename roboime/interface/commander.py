from ..communication.grsim import grSimSender
from time import time


class Commander(object):

    field = None


class SimCommander(Commander):

    def __init__(self, team):
        self.team = team
        self.sender = grSimSender()

    def step(self):
        #TODO: create command objects instead of sending updates
        packet = self.sender.new_packet()

        actions = []
        for r in self.team:
            if r.action is not None:
                actions.append(r.action)

        if len(actions) > 0:
            packet.commands.isteamyellow = self.team.is_yellow
            packet.commands.timestamp = time()
            for a in actions:
                c = packet.commands.robot_commands.add()
                c.id = a.uid
                c.kickspeedx = a.kick
                c.kickspeedz = a.chipkick
                s = a.speeds
                c.veltangent = s[0]
                c.velnormal = s[1]
                c.velangular = s[2]
                c.spinner = a.dribble > 0
                c.wheelsspeed = False

        self.sender.send_packet(packet)
