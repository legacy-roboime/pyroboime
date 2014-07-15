#!/usr/bin/env python
from roboime.clients import iris
import sys


if __name__ == '__main__':
    if (len(sys.argv) > 1 and sys.argv[1] == '--strip'):
        app = iris.IRIS(strip_commanders=True)
    else:
        app = iris.IRIS(strip_commanders=False)

    app.mainloop()
