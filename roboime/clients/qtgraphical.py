#from time import time
from time import sleep
#import sys, os
from os import path
from PyQt4 import QtGui, QtCore, uic
from collections import OrderedDict
from ..utils.geom import Point

#from . import stageview
from ..base import World
#from ..interface.updater import SimVisionUpdater
from ..interface import SimulationInterface
from ..core.skills import goto
from ..core.skills import gotoavoid
#from ..core.skills import drivetoobject
from ..core.skills import drivetoball
from ..core.skills import sampleddribble
from ..core.skills import sampledkick
from ..core.skills import followandcover
from ..core.skills import sampledchipkick
from ..core.tactics import blocker
from ..core.tactics import defender
from ..core.tactics import goalkeeper
from ..core.tactics import zickler43
from ..core.plays import autoretaliate
from ..core.plays import indirectkick
from ..core.plays import stop
from ..core.plays import obeyreferee
from ..core.plays import halt

class GraphicalWorld(World, QtCore.QMutex):

    def __init__(self, *args, **kwargs):
        World.__init__(self, *args, **kwargs)
        QtCore.QMutex.__init__(self)

    def __enter__(self):
        self.lock()
        return self

    def __exit__(self, t, v, tb):
        self.unlock()


class QtGraphicalClient(object):
    """
    This is a QT graphical interface.
    """

    def __init__(self):
        super(QtGraphicalClient, self).__init__()


        self.world = GraphicalWorld()

        self.intelligence = Intelligence(self.world)
        #self.intelligence = Intelligence(self.world, self.ui.stageView.redraw)

        self.ui = uic.loadUi(path.join(path.dirname(__file__), 'graphical.ui'))
        self.setupUI()

        self.ui.stageView.world = self.world

        self.timer = QtCore.QTimer()
        #self.timer.timeout.connect(self.ui.stageView.redraw)
        self.timer.timeout.connect(self.redraw)


        # FIXME: This should work.
        # Redraw stageview when the interface applies an update
        #self.intelligence.interface.world_updated.connect(self.ui.stageView.redraw)

        self.ui.show()

        # Start children threads
        self.intelligence.start()

        # Start redraw timer (once every 25ms)
        self.timer.start(25)

        self.ui.statusBar.hide()

    def setupUI(self):
        # Setup GUI buttons and combo boxes

        ui = {
            'cmbSelectRobotBlue': map(str, self.intelligence.individuals_blue.keys()),
            'cmbSelectRobotYellow': map(str, self.intelligence.individuals_yellow.keys()),
            'cmbSelectIndividualBlue': self.intelligence.individuals_blue[0].keys(),
            'cmbSelectIndividualYellow': self.intelligence.individuals_yellow[0].keys(),
            'cmbSelectPlayBlue': self.intelligence.plays_blue.keys(),
            'cmbSelectPlayYellow': self.intelligence.plays_yellow.keys(),
        }

        for cmb in ui:
            for i in ui[cmb]:
                getattr(self.ui, cmb).addItem(i, i)

        # Connect signals to slots
        #self.ui.cmbPenalty.currentIndexChanged.connect(self.setPenaltyKicker)
        #self.ui.cmbGoalkeeper.currentIndexChanged.connect(self.setGoalkeeper)
        self.ui.cmbSelectOutput.currentIndexChanged.connect(self.changeIntelligenceOutput)
        self.ui.cmbSelectPlayBlue.currentIndexChanged.connect(self.changePlayBlue)
        self.ui.cmbSelectRobotBlue.currentIndexChanged.connect(self.changeIndividualBlue)
        self.ui.cmbSelectIndividualBlue.currentIndexChanged.connect(self.changeIndividualBlue)
        self.ui.cmbSelectPlayYellow.currentIndexChanged.connect(self.changePlayYellow)
        self.ui.cmbSelectRobotYellow.currentIndexChanged.connect(self.changeIndividualYellow)
        self.ui.cmbSelectIndividualYellow.currentIndexChanged.connect(self.changeIndividualYellow)
        self.ui.cmbOurTeam.currentIndexChanged.connect(self.setTeamColor)
        self.ui.btnChangeSides.clicked.connect(self.changeSides)
        self.ui.actionFullscreen.triggered.connect(self.toggleFullScreen)

    def redraw(self):
        self.ui.stageView.redraw()
        w = self.intelligence.world
        self.ui.txtRefCommand.setText(str(w.referee.pretty_command))
        self.ui.txtRefStage.setText(str(w.referee.pretty_stage))
        self.ui.txtTimeLeft.setText('{:.02f}'.format((w.referee.stage_time_left or 0) / 1e6))
        self.ui.txtScoreLeft.setText(str(w.left_team.score))
        self.ui.txtTimeoutsLeft.setText(str(w.left_team.timeouts))
        self.ui.txtTimeoutTimeLeft.setText('{:.02f}'.format((w.left_team.timeout_time or 0) / 1e6))
        self.ui.txtScoreRight.setText(str(w.right_team.score))
        self.ui.txtTimeoutsRight.setText(str(w.right_team.timeouts))
        self.ui.txtTimeoutTimeRight.setText('{:.02f}'.format((w.right_team.timeout_time or 0) / 1e6))

    # GUI Functions
    def setPenaltyKicker(self):
        raise NotImplementedError

    def setGoalkeeper(self):
        raise NotImplementedError

    def changeIntelligenceOutput(self):
        raise NotImplementedError

    def changePlayBlue(self):
        self.intelligence.current_play_blue = self.intelligence.plays_blue[str(self.ui.cmbSelectPlayBlue.currentText())]

    def changeIndividualBlue(self):
        self.intelligence.current_individual_blue = self.intelligence.individuals_blue[self.ui.cmbSelectRobotBlue.currentIndex()][str(self.ui.cmbSelectIndividualBlue.currentText())]

    def changePlayYellow(self):
        self.intelligence.current_play_yellow = self.intelligence.plays_yellow[str(self.ui.cmbSelectPlayYellow.currentText())]

    def changeIndividualYellow(self):
        self.intelligence.current_individual_yellow = self.intelligence.individuals_yellow[self.ui.cmbSelectRobotYellow.currentIndex()][str(self.ui.cmbSelectIndividualYellow.currentText())]

    def setTeamColor(self):
        raise NotImplementedError

    def changeSides(self):
        raise NotImplementedError

    def hideTabs(self):
        if self.ui.tabWidget.isVisible():
            self.ui.tabWidget.setVisible(False)
            self.ui.btnTabHide.setText('Unhide')
        else:
            self.ui.tabWidget.setVisible(True)
            self.ui.btnTabHide.setText('Hide')

        # Reset camera position and scale, so it fits the screen
        self.ui.stageView.fit()

    def toggleFullScreen(self, activate):
        if self.ui.windowState() & QtCore.Qt.WindowFullScreen:
            self.ui.showNormal()
            self.ui.dockSetup.show()
            self.ui.menuBar.show()
            #self.ui.statusBar.show()
        else:
            self.ui.showFullScreen()
            self.ui.dockSetup.hide()
            self.ui.menuBar.show()
            #self.ui.statusBar.hide()
        QtGui.QApplication.processEvents()
        self.ui.stageView.fit()

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

    def __init__(self, world, count_robot=6):
        super(Intelligence, self).__init__()

        class Dummy(object):
            def step(self):
                pass
        self.stop = False
        self.world = world
        self.skill = None
        self.interface = SimulationInterface(self.world)

        self.individual = lambda robot: OrderedDict([
            ('(none)', Dummy()),
            ('Go To', goto.Goto(robot, target=Point(0, 0))),
            ('Go To Avoid', gotoavoid.GotoAvoid(robot, target=Point(0, 0), avoid=self.world.ball)),
            #('Drive To Object', drivetoobject.DriveToObject(robot)),
            ('Drive To Ball', drivetoball.DriveToBall(robot, lookpoint=robot.enemy_goal)),
            ('Sampled Dribble', sampleddribble.SampledDribble(robot, lookpoint=robot.enemy_goal)),
            ('Sampled Kick', sampledkick.SampledKick(robot, lookpoint=robot.enemy_goal)),
            ('Follow And Cover', followandcover.FollowAndCover(robot, follow=robot.goal, cover=self.world.ball)),
            ('Sampled Chip Kick', sampledchipkick.SampledChipKick(robot, lookpoint=robot.enemy_goal)),
            ('Blocker', blocker.Blocker(robot, arc=0)),
            ('Goalkeeper', goalkeeper.Goalkeeper(robot, angle=30, aggressive=True)),
            ('Zickler43', zickler43.Zickler43(robot)),
            ('Defender', defender.Defender(robot, enemy=self.world.ball)),
        ])
        self.plays = lambda team: OrderedDict([
            ('(none)', Dummy()),
            ('Auto Retaliate', autoretaliate.AutoRetaliate(team, 0)),
            ('Stop', stop.Stop(team, 0)),
            ('Indirect Kick', indirectkick.IndirectKick(team, 0)),
            ('Obey Referee', obeyreferee.ObeyReferee(autoretaliate.AutoRetaliate(team, 0), 0)),
            ('Halt', halt.Halt(team)),
        ])

        self.individuals_blue = dict((i, self.individual(self.world.blue_team[i])) for i in range(count_robot))
        self.individuals_yellow = dict((i, self.individual(self.world.yellow_team[i])) for i in range(count_robot))

        self.plays_blue = self.plays(self.world.blue_team)
        self.plays_yellow = self.plays(self.world.yellow_team)

        self.current_play_blue = Dummy()
        self.current_play_yellow = Dummy()

        self.current_individual_blue = Dummy()
        self.current_individual_yellow = Dummy()

    def _loop(self):
        #        #self.skill = followandcover.FollowAndCover(r, follow=self.world.ball, cover=self.world.blue_team[3])
        #        #self.skill = sampledkick.SampledKick(r, lookpoint=self.world.left_goal)
        #        #self.skill = sampleddribble.SampledDribble(r, lookpoint=self.world.left_goal)
        #        #self.skill = drivetoball.DriveToBall(r, lookpoint=self.world.left_goal)
        #        #self.skill = gotoavoid.GotoAvoid(r, target=Point(0, 0), avoid=self.world.ball)
        #        #self.skill = goto.Goto(r, target=Point(0, 0))
        #        #self.skill = goto.Goto(r, x=r.x, y=r.y, angle=90, speed=1, ang_speed=10)
        #    self.skill.step()
        #for play in self.plays.itervalues():
        #    play.step()
        self.current_play_blue.step()
        self.current_play_yellow.step()

        self.current_individual_blue.step()
        self.current_individual_yellow.step()

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
            from traceback import print_exc
            print_exc()
            raise
        finally:
            self.interface.stop()


class App(QtGui.QApplication):

    def __init__(self, argv):
        super(App, self).__init__(argv)
        self.window = QtGraphicalClient()
        self.aboutToQuit.connect(self.window.teardown)
