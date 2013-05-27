from time import time
import sys, os
from PyQt4 import QtGui, QtCore, uic

from . import stageview
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


class Cute(QtGui.QMainWindow):
    """
    This is a QT graphical interface.
    """

    def __init__(self):
        super(Cute, self).__init__()
        
        self.ui = uic.loadUi(os.path.join(os.path.dirname(__file__), './GraphicalIntelligence.ui'))        

        self.ui.show()

        self.world = World()
        self.interface = SimulationInterface(self.world)
        self.timestamp1 = time()
        self.timestamp2 = time()
        self.skill = None

        self.interface.start()

    def loop(self):
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

        self.interface.step()

