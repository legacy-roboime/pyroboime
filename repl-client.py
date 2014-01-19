#!/usr/bin/env python
from sys import argv
from roboime.clients import repl

if __name__ == '__main__':
    app = repl.Main(
        show_fps=('--fps' in argv),
        show_perf=('--perf' in argv),
    )
    app.mainloop()

