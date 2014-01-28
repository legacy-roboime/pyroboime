#!/usr/bin/env python
from sys import argv
from roboime.clients import demo_versus

if __name__ == '__main__':
    app = demo_versus.Demo()
    app.mainloop()

