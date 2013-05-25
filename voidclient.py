#!/usr/bin/env python
from sys import argv
from roboime.clients import simple

if __name__ == '__main__':
    show_fps = False
    if len(argv) > 1:
        if argv[1] == '--fps':
            show_fps = True
    app = simple.Simple(show_fps=show_fps)
    app.mainloop()
else:
    raise Exception('This is not a module.')

