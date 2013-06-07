#from time import time
from time import sleep
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
#from ..core.plays import autoretaliate
from ..core.plays import stop


class GraphicalWorld(World, QtCore.QMutex):

    def __init__(self, *args, **kwargs):
        World.__init__(self, *args, **kwargs)
        QtCore.QMutex.__init__(self)

    def __enter__(self):
        self.lock()
        return self

    def __exit__(self, t, v, tb):
        self.unlock()


class QtGraphicalClient(QtGui.QMainWindow):
    """
    This is a QT graphical interface.
    """

    def __init__(self):
        super(QtGraphicalClient, self).__init__()


        self.world = GraphicalWorld()

        self.intelligence = Intelligence(self.world)
        #self.intelligence = Intelligence(self.world, self.ui.stageView.redraw)

        self.ui = uic.loadUi(path.join(path.dirname(__file__), './GraphicalIntelligence.ui'))
        self.setupUI()

        self.ui.stageView.world = self.world

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.ui.stageView.redraw)

        # FIXME: This should work.
        # Redraw stageview when the interface applies an update
        #self.intelligence.interface.world_updated.connect(self.ui.stageView.redraw)

        self.ui.show()

        # Start children threads
        self.intelligence.start()

        # Start redraw timer (once every 25ms)
        self.timer.start(25)

    def setupUI(self):
        # Setup GUI buttons and combo boxes

        # Tactics ComboBoxes
        self.ui.cmbSelectTacticOurs.addItem('Zickler43', 'zickler43')
        self.ui.cmbSelectTacticOurs.addItem('Goleiro', 'gkpr')
        self.ui.cmbSelectTacticOurs.addItem('Defesa 1', 'defU32')

        self.ui.cmbSelectTacticTheirs.addItem('Zickler43', 'zickler43T')
        self.ui.cmbSelectTacticTheirs.addItem('Goleiro', 'gkprT')
        self.ui.cmbSelectTacticTheirs.addItem('Defesa 1', 'defT32')

        # Plays ComboBoxes
        self.ui.cmbSelectPlayOurs.addItem('Halt', 'haltU')
        self.ui.cmbSelectPlayOurs.addItem('CBR2011', 'cbr')
        #FIXME: Needs to format string 'Retaliacao' to accept tilde and cedilla
        self.ui.cmbSelectPlayOurs.addItem('Retaliacao', 'retaliateU')
        self.ui.cmbSelectPlayOurs.addItem('Minmax', 'minimax2')
        self.ui.cmbSelectPlayOurs.addItem('Obedecer Juiz', 'refereeU')

        self.ui.cmbSelectPlayTheirs.addItem('Halt', 'haltT')
        self.ui.cmbSelectPlayTheirs.addItem('CBR2011', 'cbr2')
        self.ui.cmbSelectPlayTheirs.addItem('Retaliacao', 'retaliateT')
        self.ui.cmbSelectPlayTheirs.addItem('Obedecer Juiz', 'refereeT')

        # Mode ComboBox
        self.ui.cmbSelectMode.addItem('Play', 'PLAY')
        self.ui.cmbSelectMode.addItem('Tatica', 'TACTIC')
        self.ui.cmbSelectMode.addItem('Skill', 'SKILL')

        # Connect signals to slots
        self.ui.cmbPenalty.currentIndexChanged.connect(self.setPenaltyKicker)
        self.ui.cmbGoalkeeper.currentIndexChanged.connect(self.setGoalkeeper)
        self.ui.cmbSelectOutput.currentIndexChanged.connect(self.changeIntelligenceOutput)
        self.ui.cmbSelectPlayOurs.currentIndexChanged.connect(self.changePlayUs)
        self.ui.cmbSelectTacticOurs.currentIndexChanged.connect(self.changeTacticUs)
        self.ui.cmbSelectPlayTheirs.currentIndexChanged.connect(self.changePlayThem)
        self.ui.cmbSelectTacticTheirs.currentIndexChanged.connect(self.changeTacticThem)
        self.ui.cmbSelectMode.currentIndexChanged.connect(self.changeMode)
        self.ui.cmbOurTeam.currentIndexChanged.connect(self.setTeamColor)
        self.ui.btnChangeSides.clicked.connect(self.changeSides)

    # GUI Functions
    def setPenaltyKicker(self):
        pass

    def setGoalkeeper(self):
        pass

    def changeIntelligenceOutput(self):
        pass

    def changePlayUs(self):
        pass

    def changeTacticUs(self):
        pass

    def changePlayThem(self):
        pass

    def changeTacticThem(self):
        pass

    def changeMode(self):
        pass

    def setTeamColor(self):
        pass

    def changeSides(self):
        pass

    def teardown(self):
        """Tear down actions."""

        self.intelligence.stop = True

        # wait for it to stop, Qt doesn't have a join method appearently.
        while self.intelligence.isRunning():
            pass

    def closeEvent(self, event):
        print 'closeEvent'
        self.teardown()
        event.accept()



class Intelligence(QtCore.QThread):

    def __init__(self, world):
        super(Intelligence, self).__init__()
        self.stop = False
        self.world = world
        self.skill = None
        self.interface = SimulationInterface(self.world)
        self.plays = {
            #'autoretal_b': autoretaliate.AutoRetaliate(world.blue_team, 0),
            #'autoretal_y': autoretaliate.AutoRetaliate(world.yellow_team, 0),
            'stop_b': stop.Stop(world.blue_team, 0),
            'stop_y': stop.Stop(world.yellow_team, 0),
        }

    def _loop(self):
        #if 2 in self.world.blue_team:
        #    r = self.world.blue_team[2]
        #    r.max_speed = 2.0
        #    if self.skill is None:
        #        self.skill = sampledchipkick.SampledChipKick(r, lookpoint=self.world.left_goal)
        #        #self.skill = followandcover.FollowAndCover(r, follow=self.world.ball, cover=self.world.blue_team[3])
        #        #self.skill = sampledkick.SampledKick(r, lookpoint=self.world.left_goal)
        #        #self.skill = sampleddribble.SampledDribble(r, lookpoint=self.world.left_goal)
        #        #self.skill = drivetoball.DriveToBall(r, lookpoint=self.world.left_goal)
        #        #self.skill = gotoavoid.GotoAvoid(r, target=Point(0, 0), avoid=self.world.ball)
        #        #self.skill = goto.Goto(r, target=Point(0, 0))
        #        #self.skill = goto.Goto(r, x=r.x, y=r.y, angle=90, speed=1, ang_speed=10)
        #    self.skill.step()
        for play in self.plays.itervalues():
            play.step()

        with self.world:
            self.interface.step()

    def run(self):
        self.interface.start()
        try:
            while not self.stop:
                self._loop()
                sleep(10e-3)
        except:
            print 'Bad things happened'
            raise
        finally:
            self.interface.stop()


class App(QtGui.QApplication):

    def __init__(self, argv):
        super(App, self).__init__(argv)
        self.window = QtGraphicalClient()
        self.aboutToQuit.connect(self.window.teardown)
