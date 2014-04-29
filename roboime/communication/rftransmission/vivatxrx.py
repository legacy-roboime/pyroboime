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
import usb.core
import time

from . import Transmitter

class VIVATxRx(Transmitter):
    """
    This class implements a thin wrapper around the RF12 USB transmitter
    we currently (as of july 2013) use to transmit commands to the robots.
    """

    # XXX: do send a new packet before this delay
    #      this was made due to too many packets clogging
    #      the usb transmitter
    delay = 0.05

    def __init__(self, id_vendor=5824, id_product=1500, verbose=False):
        super(VIVATxRx, self).__init__()
        try:
            self.transmitter = usb.core.find(idVendor=id_vendor, idProduct=id_product)
        except AttributeError:
            self.transmitter = None
        except ValueError:
            self.transmitter = None
        if self.transmitter is not None:
            self.transmitter.set_configuration()
        self.is_working = self.transmitter is not None
        self.verbose = verbose
        self.last_sent = time.time()

    def send(self, array):
        now = time.time()
        if now - self.last_sent < self.delay:
            # too soon
	     		
            return 0
        else:
            self.last_sent = now

        if self.verbose:
            print self.is_busy
        if (not self.is_busy) and self.is_working:
	    
            return self.transmitter.ctrl_transfer(5696, 3, 0, 0, array)
        else:
            return -1

    def receive(self):
        if self.verbose:
            print self.is_busy
        sizev =  self.transmitter.ctrl_transfer(5824, 4, 3, 0, 8)
        payload_length = sizev[1]
        data = self.transmitter.ctrl_transfer(5824, 5, payload_length, 0, payload_length)
        return data

    @property
    def is_busy(self):
        if not self.is_working:
            return False
        busy = self.transmitter.ctrl_transfer(5824, 4, 0, 0, 8)
        return busy[0] == 1
