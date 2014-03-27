from roboime.communication.rftransmission.vivatxrx import VIVATxRx

if __name__ == "__main__":
    while True:
        tr = VIVATxRx()
        print tr.receive()
