#from time import time
#import sys, os
from os import path
from PyQt4 import QtGui, QtCore, uic

#from . import stageview
from ..base import World
#from ..interface.updater import SimVisionUpdater
from ..interface import SimulationInterface
#from ..core.skills import goto
#from ..core.skills import gotoavoid
#from ..core.skills import drivetoobject
#from ..core.skills import drivetoball
#from ..core.skills import sampleddribble
#from ..core.skills import sampledkick
#from ..core.skills import followandcover
from ..core.skills import sampledchipkick
from .qtutils import Lock


class GraphicalWorld(World, Lock):

    def __init__(self, *args, **kwargs):
        World.__init__(self, *args, **kwargs)
        Lock.__init__(self)

    def __enter__(self):
        Lock.__enter__(self)
        return self


class QtGraphicalClient(QtGui.QMainWindow):
    """
    This is a QT graphical interface.
    """

    def __init__(self):
        super(QtGraphicalClient, self).__init__()

        self.world = GraphicalWorld()

        self.ui = uic.loadUi(path.join(path.dirname(__file__), './GraphicalIntelligence.ui'))
        self.ui.stageView.world = self.world

        # FIXME: This should work.
        # Redraw stageview when the interface applies an update
        #self.intelligence.interface.world_updated.connect(self.ui.stageView.redraw)

        self.intelligence = Intelligence(self.world, self.ui.stageView.redraw)

        self.ui.show()

        # Start children threads
        self.intelligence.start()


class Intelligence(QtCore.QThread):
    def __init__(self, world, redraw_callback=lambda: None):
        super(Intelligence, self).__init__()
        self.world = world
        self.skill = None
        self.interface = SimulationInterface(self.world)
        self.redraw_callback = redraw_callback

    def _loop(self):
        if 2 in self.world.blue_team:
            r = self.world.blue_team[2]
            r.max_speed = 2.0
            if self.skill is None:
                self.skill = sampledchipkick.SampledChipKick(r, lookpoint=self.world.left_goal)
                #self.skill = followandcover.FollowAndCover(r, follow=self.world.ball, cover=self.world.blue_team[3])
                #self.skill = sampledkick.SampledKick(r, lookpoint=self.world.left_goal)
                #self.skill = sampleddribble.SampledDribble(r, lookpoint=self.world.left_goal)
                #self.skill = drivetoball.DriveToBall(r, lookpoint=self.world.left_goal)
                #self.skill = gotoavoid.GotoAvoid(r, target=Point(0, 0), avoid=self.world.ball)
                #self.skill = goto.Goto(r, target=Point(0, 0))
                #self.skill = goto.Goto(r, x=r.x, y=r.y, angle=90, speed=1, ang_speed=10)
            self.skill.step()
        with self.world:
            self.interface.step()
        self.redraw_callback()

    def run(self):
        self.interface.start()
        try:
            while True:
                self._loop()
        except:
            print 'Bad things happened'
            raise
        finally:
            self.interface.stop()
