#!/usr/bin/env python
from roboime.clients import server

if __name__ == '__main__':
    app = server.Server()
    app.mainloop()
