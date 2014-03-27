from roboime.communication import grsim
from roboime.communication.rftransmission.vivatxrx import VIVATxRx
from time import time
from math import sin, cos
from roboime.utils.pidcontroller import PidController


def speed_from_byte(x, max=64.):
    #print x & 128 >> 7
    sign = -(((x & 128) >> 7) * 2 - 1)
    if sign == -1:
        modulo = (~x & 127) + 1
    else:
        modulo = x
    return sign * modulo * max / 127

if __name__ == "__main__":
    sender = grsim.grSimSender(('192.168.91.163', 20011))
    tr = VIVATxRx()
    while True:
        data = tr.receive()
        #print data
        if not len(data):
            continue
        else:
            print data

        packet = sender.new_packet()

        packet.commands.isteamyellow = True
        packet.commands.timestamp = time()
        for i in xrange(6):
            c = packet.commands.robot_commands.add()
            c.id = i
            chip_angle = 45
            kick = speed_from_byte(data[3 + 7 * i + 6], 10.)
            #print data[3 + 7 * i + 5], " ", kick
            chipkick = 0
            if kick < 0:
                chipkick = kick
                kick = 0

            c.kickspeedz = (chipkick or 0.0) * sin(chip_angle)
            if c.kickspeedz > 0:
                c.kickspeedx = chipkick * cos(chip_angle)
            else:
                c.kickspeedx = (kick or 0.0) * 5
            c.veltangent = 0
            c.velnormal = 0
            c.velangular = 0
            c.spinner = (data[3 + 7 * i + 5]) > 0
            c.wheelsspeed = True

            c.wheel1 = -speed_from_byte(data[3 + 7 * i + 1])
            c.wheel2 = -speed_from_byte(data[3 + 7 * i + 2])
            c.wheel3 = -speed_from_byte(data[3 + 7 * i + 3])
            c.wheel4 = -speed_from_byte(data[3 + 7 * i + 4])

            pass#print "wheels: ", c.wheel1, c.wheel2, c.wheel3, c.wheel4
        sender.send_packet(packet)
