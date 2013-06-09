#!/usr/bin/env python
from sys import argv
from roboime.clients import simple

if __name__ == '__main__':
    app = simple.Simple(
        show_fps=('--fps' in argv),
        show_perf=('--perf' in argv),
    )
    app.mainloop()

