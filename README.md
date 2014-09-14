RoboIME's Artificial Intelligence
=================================

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

Web interface
-------------

There is an ongoing effort to use [ssl-webclient](https://github.com/roboime/ssl-webclient) as an interface for this
software.
Various changes are expected and lots of requirements should be dropped to further simplify this project.

License
-------

This software is licensed under the [AGPL](http://www.gnu.org/licenses/agpl-3.0.html), a copy of this license can
be found on the [LICENSE](LICENSE) file.

__There is an aditional clause for using this code on competitions:__

- Any derived work from this software must be released under the same license and terms at least before the next
  instance of the competition which it was used.
  For example, if you use this project for the 10th Foo competition you must release the derived software
  used on that competition before the 11th Foo competition.

The reason for the term above is to promote collaboration, help starting teams and also maintain competitiveness.

This is an experimental clause that may be modified in the future, any critique is appreciated.

How to's
--------

To run intelligence and transmission and control robots with joystick:
 1. Plug the transmission on the computer
 2. Run one of the following:
  a. To run with the ssl-vision client(camera needed):
    $ cd ~/ssl-vision/bin
    $ ./vision -s
  b. To run with grSim:
    $ grsim
    then set it to send the position of the robots on port 10002
 3. At ~/pyroboime run:
    $ ./iris.py
    -------------
    >>> set_individual('blue',0,'joystick')
    >>> individuals()

  TO get help with iris.py commands:
    >>> mayday()

  To get robots that are on the 'world':
    >>> world.robots

Important files location
------------------------

joystick commands definition:
  ~/pyroboime/roboime/core/skill/joystick.py

communication files:
  roboime/communication/rftransmission/vivatxrx.py

transmission package definition:
  roboime/interface/commander.py
                    tx2013commander
                    tx2014commander
