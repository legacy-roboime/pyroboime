#!/usr/bin/env python -O
from sys import argv
from roboime.clients import cute

if __name__ == '__main__':
    show_fps = False
    if len(argv) > 1:
        if argv[1] == '--fps':
            show_fps = True
    app = cute.Cute()
    app.mainloop()
else:
    raise Exception('This is not a module.')

