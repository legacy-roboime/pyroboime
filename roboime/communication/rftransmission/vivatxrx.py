import usb.core

from . import Transmitter

class VIVATxRx(Transmitter):
    '''
    This class implements a thin wrapper around the RF12 USB transmitter
    we currently (as of july 2013) use to transmit commands to the robots.
    '''
    def __init__(self, id_vendor=5824, id_product=1500):
        super(VIVATxRx, self).__init__()
        try:
            self.transmitter = usb.core.find(idVendor=id_vendor, idProduct=id_product)
        except ValueError:
            self.transmitter = None
        if self.transmitter is not None:
            self.transmitter.set_configuration()
        self.is_working = self.transmitter is None

    def send(self, array):
        print self.is_busy
        if (not self.is_busy) and self.is_working:
            return self.transmitter.ctrl_transfer(5696, 3, 0, 0, array)
        else:
            return -1

    @property
    def is_busy(self):
        if not self.is_working:
            return False
        busy = self.transmitter.ctrl_transfer(5824, 4, 0, 0, 8)
        return busy[0] == 1
