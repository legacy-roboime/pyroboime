#
# Copyright (C) 2014 RoboIME
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
import sys
import glob
import serial
import time

from . import Transmitter
from ...utils.log import Log


def serial_ports():
    """Lists serial ports

    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of available serial ports
    """
    if sys.platform.startswith('win'):
        ports = ['COM' + str(i + 1) for i in range(256)]

    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this is to exclude your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')

    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')

    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

class SerialTxRx(Transmitter):
    """
    This class implements a Serial trasmitter for the
    brand new transmitter.
    """

    # XXX: do not send a new packet before this delay
    #      this was made due to too many packets clogging
    #      the usb transmitter
    delay = 0.05


    def __init__(self, address=None, verbose=False):
        super(SerialTxRx, self).__init__()

        # defining the address dinamically
        if address is None:
            if sys.platform.startswith('darwin'):
                available_addresses = serial_ports()
                for addr in available_addresses:
                    if 'usbmodem' in addr:
                        address = addr;


        try:
            self.transmitter = serial.Serial(address)
        except AttributeError:
            self.transmitter = None
        except ValueError:
            self.transmitter = None
        self.is_working = self.transmitter is not None
        self.verbose = verbose
        self.last_sent = time.time()
        self.log = Log('interface')

    def send(self, array):
        now = time.time()
        if now - self.last_sent < self.delay:
            # too soon
            return 0

        else:
            self.last_sent = now

        if (not self.is_busy) and self.is_working:
            while(len(array) < 64):
                array.append(0x00)
            self.log.debug(' '.join('{:02x}'.format(a) for a in array))
            return self.transmitter.write(array)

        else:
            return -1

    def receive(self):
        if self.verbose:
            #print self.is_busy
            pass
        #sizev =  self.transmitter.ctrl_transfer(5824, 4, 3, 0, 8)

        data = self.transmitter.read(32)
        return data

    @property
    def is_busy(self):
        if not self.is_working:
            return False
        busy = self.transmitter.inWaiting()
        return busy > 0
