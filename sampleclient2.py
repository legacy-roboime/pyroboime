#!/usr/bin/env python -O
from roboime.clients import simple

if __name__ == '__main__':
    app = simple.Simple(show_fps=False)
    app.mainloop()
else:
    raise Exception('This is not a module.')

