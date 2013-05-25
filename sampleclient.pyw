#!/usr/bin/env python
from roboime.clients import view

if __name__ == '__main__':
    app = view.View()
    app.mainloop()
else:
    raise Exception('This is not a module.')

