RoboIME Artificial Intelligence
===============================

This is an attempt to develop the intelligence project on python.
Python 2 is required due to google.protobuf, aside from that, the code is designed to be mostly Python 3 compatible.

If running 64-bit Python, the following , 64-bit packages for numpy and scipy are also needed. these cna be found in:

- http://www.lfd.uci.edu/~gohlke/pythonlibs/#scipy
- http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy

Great Python debugger for Windows users (even though it is meant to be a platform-independent debugger):

- Winpdb (http://winpdb.org/download/)
- Which needs wxPython (http://sourceforge.net/projects/wxpython/?source=dlp)
- How-to:
  1. install wxPython
  2. create a folder, then extract and install Winpdb
  3. To add a breakpoint:
    - add the following line before the "point to be broken": import rpdb2; rpdb2.start\_embedded\_debugger("123")
      note: that 123 is a customizable password, which will be retrieved later
    - open winpdb GUI.
    - file > attach...
    - select "localhost" and the correspondent PID
    - type 123 (or the password that matches with -3.1-)
    - voilà

The Qt client requires PyQt4 to work. 64-bit windows users are advised to install the binaries provided by Riverbank.

To use a joystick (xbox controller, attack 3 or maxprint) pygame is required.
