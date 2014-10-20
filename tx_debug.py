import time
from functools import partial
from roboime.communication.rftransmission.vivatxrx import VIVATxRx


def transform(pkg):
    return map(partial(int, base=16), pkg.split())

faulty = 'fe 00 63 7f 00 00 00 00 00 00 7f 00 00 00 00 00 00 7f 00 00 00 00 00 00 7f 00 00 00 00 00 00 7f 00 00 00 00 00 00 7f 00 00 00 00 00 00 37'

#array = [254, 0, 44, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 55]
array_a = [254, 0, 88, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 2, 0, 4, 0, 4, 70, 80, 3, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 55]
#array_a = '\xfe\x00\x58' + '\x02\x01\x02\x00\x07\x00\x00' * 6 + '\x37'
array_b = [254, 0, 99, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 55]
#array_b = [254, 0, 88, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 1, 0, 0, 3, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 55]
#array_a = [254, 0, 88, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 130, 0, 0, 0, 60, 0, 0, 3, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 55]
#array_b = array_a
array_b = transform(faulty)
tr = VIVATxRx()

i = 0
while True:
    print list(array_a)
    tr.send(array_a)
    time.sleep(0.010)
    if i == 10:
        for _ in range(10):
            print list(array_b)
            tr.send(array_b)
            time.sleep(0.010)
        i = 0
    else:
        i += 1
