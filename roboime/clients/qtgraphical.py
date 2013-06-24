#from time import time
from time import sleep
#import sys, os
from os import path
from collections import defaultdict
from PyQt4 import QtGui, QtCore, uic
from collections import OrderedDict
from ..utils.geom import Point

#from . import stageview
from ..base import World
#from ..interface.updater import SimVisionUpdater
from ..interface import SimulationInterface, TxInterface
from ..core import Dummy
from ..core.skills import goto
from ..core.skills import gotoavoid
from ..core.skills import drivetoobject
from ..core.skills import drivetoball
from ..core.skills import sampleddribble
from ..core.skills import sampledkick
from ..core.skills import followandcover
from ..core.skills import sampledchipkick
from ..core.skills import kickto
try:
    from ..core.skills import joystick
except ImportError:
    joystick = None
from ..core.tactics import blocker
from ..core.tactics import defender
from ..core.tactics import goalkeeper
from ..core.tactics import zickler43
from ..core.tactics import executepass
from ..core.tactics import receivepass
from ..core.plays import autoretaliate
from ..core.plays import indirectkick
from ..core.plays import stop
from ..core.plays import obeyreferee
from ..core.plays import halt
from ..core.plays import ifrit

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

    def __init__(self, **kwargs):
        super(QtGraphicalClient, self).__init__()

        self.world = GraphicalWorld()

        self.intelligence = Intelligence(self.world, **kwargs)
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
        self.useSimulation = True
        self.resetPatterns()

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

        # Create the robot widget

        # Connect signals to slots
        #self.ui.cmbPenalty.currentIndexChanged.connect(self.setPenaltyKicker)
        #self.ui.cmbGoalkeeper.currentIndexChanged.connect(self.setGoalkeeper)
        #self.ui.cmbSelectOutput.currentIndexChanged.connect(self.changeIntelligenceOutput)
        self.ui.cmbSelectPlayBlue.currentIndexChanged.connect(self.changePlayBlue)
        self.ui.cmbSelectRobotBlue.currentIndexChanged.connect(self.changeIndividualBlue)
        self.ui.cmbSelectIndividualBlue.currentIndexChanged.connect(self.changeIndividualBlue)
        self.ui.cmbSelectPlayYellow.currentIndexChanged.connect(self.changePlayYellow)
        self.ui.cmbSelectRobotYellow.currentIndexChanged.connect(self.changeIndividualYellow)
        self.ui.cmbSelectIndividualYellow.currentIndexChanged.connect(self.changeIndividualYellow)
        self.ui.cmbOurTeam.currentIndexChanged.connect(self.setTeamColor)
        self.ui.btnChangeSides.clicked.connect(self.changeSides)
        self.ui.actionFullscreen.triggered.connect(self.toggleFullScreen)
        self.ui.actionSetupDock.toggled.connect(self.toggleSetupDock)
        #self.ui.dockSetup.visibilityChanged.connect(self.toggleSetupDockAction)
        self.ui.actionRobotDock.toggled.connect(self.toggleRobotDock)
        #self.ui.dockRobot.visibilityChanged.connect(self.toggleRobotDockAction)

        self.ui.rbtSimulation.toggled.connect(self.toggleSimulation)
        self.ui.rbtTransmission.toggled.connect(self.toggleSimulation)
        
        # Mappings
        self.ui.cmbSelectUidYellow.currentIndexChanged.connect(self.selectFirmwareFromUidYellow)
        self.ui.cmbSelectUidBlue.currentIndexChanged.connect(self.selectFirmwareFromUidBlue)
        self.ui.cmbSelectFirmwareIdYellow.currentIndexChanged.connect(self.setFirmwareIdYellow)
        self.ui.cmbSelectFirmwareIdBlue.currentIndexChanged.connect(self.setFirmwareIdBlue)
        self.ui.btnDefaultBlue.clicked.connect(self.setDefaultMappingBlue)
        self.ui.btnDefaultYellow.clicked.connect(self.setDefaultMappingYellow)

        self.ui.cmbKickYellow.currentIndexChanged.connect(self.selectSliderFromUidYellow)
        self.ui.cmbKickBlue.currentIndexChanged.connect(self.selectSliderFromUidBlue)

        self.ui.sliderKickBlue.valueChanged.connect(self.setKickPowerBlue)
        self.ui.sliderKickYellow.valueChanged.connect(self.setKickPowerYellow)

        for i in range(self.intelligence.count_robot):
            self.ui.cmbRobotID.addItem(str(i))

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

        uid = self.ui.cmbRobotID.currentIndex()
        team = w.blue_team if self.ui.cmbRobotTeam.currentText() == 'Azul' else w.yellow_team
        robot = team[uid]
        self.ui.txtRobotPosition.setText('{: 6.2f}, {: 6.2f}'.format(robot.x, robot.y))
        if robot.angle is None:
            self.ui.txtRobotAngle.setText('--')
        else:
            self.ui.txtRobotAngle.setText('{: 6.2f}'.format(robot.angle))
        if robot.speed is None:
            self.ui.txtRobotSpeed.setText('--')
        else:
            self.ui.txtRobotSpeed.setText('{: 6.2f}, {: 6.2f}'.format(*robot.speed))
        if robot.acceleration is None:
            self.ui.txtRobotAcceleration.setText('--')
        else:
            self.ui.txtRobotAcceleration.setText('{: 6.2f}, {: 6.2f}'.format(*robot.acceleration))
        self.ui.txtRobotCanKick.setText(str(robot.can_kick))

    # GUI Functions

    def selectSliderFromUidBlue(self):
        uid = int(self.ui.cmbKickBlue.currentText())
        self.ui.sliderKickBlue.setValue(self.intelligence.kick_mapping_blue[uid])
        #print self.intelligence.kick_mapping_blue
    
    def setKickPowerBlue(self):
        uid = int(self.ui.cmbKickBlue.currentText())
        self.intelligence.kick_mapping_blue[uid] = int(self.ui.sliderKickBlue.value())
        if self.intelligence.kick_mapping_blue[uid] > 0:
            self.world.blue_team[uid].can_kick = True
        else:
            self.world.blue_team[uid].can_kick = False
        #print self.intelligence.kick_mapping_blue

    def selectSliderFromUidYellow(self):
        uid = int(self.ui.cmbSelectUidYellow.currentText())
        self.ui.sliderKickBlue.setValue(self.intelligence.kick_mapping_yellow[uid])
        #print self.intelligence.kick_mapping_yellow
   
    def setKickPowerYellow(self):
        uid = int(self.ui.cmbKickBlue.currentText())
        self.intelligence.kick_mapping_yellow[uid] = int(self.ui.sliderKickYellow.value())
        if self.intelligence.kick_mapping_yellow[uid] > 0:
            self.world.yellow_team[uid].can_kick = True
        else:
            self.world.yellow_team[uid].can_kick = False
        #print self.intelligence.kick_mapping_yellow
    
    def selectFirmwareFromUidYellow(self):
        uid = int(self.ui.cmbSelectUidYellow.currentText())
        if uid in self.intelligence.mapping_yellow:
            self.ui.cmbSelectFirmwareIdYellow.setCurrentIndex(self.intelligence.mapping_yellow[uid]+1)
        else:
            self.ui.cmbSelectFirmwareIdYellow.setCurrentIndex(0)

    def setFirmwareIdYellow(self):
        try:
            uid = int(self.ui.cmbSelectUidYellow.currentText())
            self.intelligence.mapping_yellow[uid] = int(self.ui.cmbSelectFirmwareIdYellow.currentText())
        except:
            if uid in self.intelligence.mapping_yellow:
                self.intelligence.mapping_yellow.pop(uid)
        #print self.intelligence.mapping_yellow

    def selectFirmwareFromUidBlue(self):
        uid = int(self.ui.cmbSelectUidBlue.currentText())
        if uid in self.intelligence.mapping_blue:
            self.ui.cmbSelectFirmwareIdBlue.setCurrentIndex(self.intelligence.mapping_blue[uid]+1)
        else:
            self.ui.cmbSelectFirmwareIdBlue.setCurrentIndex(0)

    def setFirmwareIdBlue(self):
        try:
            uid = int(self.ui.cmbSelectUidBlue.currentText())
            self.intelligence.mapping_blue[uid] = int(self.ui.cmbSelectFirmwareIdBlue.currentText())
        except:
            if uid in self.intelligence.mapping_blue:
                self.intelligence.mapping_blue.pop(uid)
        #print self.intelligence.mapping_blue

    def setDefaultMappingBlue(self):
        self.intelligence.mapping_yellow.clear()
        self.intelligence.mapping_blue.clear()
        for r in self.intelligence.world.blue_team:
            self.intelligence.mapping_blue[r.uid] = r.uid
        uid = int(self.ui.cmbSelectUidBlue.currentText())
        if uid in self.intelligence.mapping_blue:
            self.ui.cmbSelectFirmwareIdBlue.setCurrentIndex(self.intelligence.mapping_blue[uid]+1)
        self.ui.cmbSelectFirmwareIdYellow.setCurrentIndex(0)

    def setDefaultMappingYellow(self):
        self.intelligence.mapping_yellow.clear()
        self.intelligence.mapping_blue.clear()
        for r in self.intelligence.world.yellow_team:
            self.intelligence.mapping_yellow[r.uid] = r.uid
        uid = int(self.ui.cmbSelectUidYellow.currentText())
        if uid in self.intelligence.mapping_yellow:
            self.ui.cmbSelectFirmwareIdYellow.setCurrentIndex(self.intelligence.mapping_yellow[uid]+1)
        self.ui.cmbSelectFirmwareIdBlue.setCurrentIndex(0)

    def setPenaltyKicker(self):
        raise NotImplementedError

    def setGoalkeeper(self):
        raise NotImplementedError

    def changeIntelligenceOutput(self):
        #mutex: no mutex to lock like in cpp
        if self.ui.cmbSelectOutput.currentIndex == 0:
            self.useSimulation = True
        else:
            self.useSimutalion = False
        self.resetPatterns()

    def changePlayBlue(self):
        self.intelligence.current_play_blue = self.intelligence.plays_blue[str(self.ui.cmbSelectPlayBlue.currentText())]

    def changeIndividualBlue(self):
        self.intelligence.current_individual_blue = self.intelligence.individuals_blue[self.ui.cmbSelectRobotBlue.currentIndex()][str(self.ui.cmbSelectIndividualBlue.currentText())]

    def changePlayYellow(self):
        self.intelligence.current_play_yellow = self.intelligence.plays_yellow[str(self.ui.cmbSelectPlayYellow.currentText())]

    def changeIndividualYellow(self):
        self.intelligence.current_individual_yellow = self.intelligence.individuals_yellow[self.ui.cmbSelectRobotYellow.currentIndex()][str(self.ui.cmbSelectIndividualYellow.currentText())]

    #XXX: not implemented in c++
    def setTeamColor(self):
        raise NotImplementedError

    def changeSides(self):
        self.intelligence.world.switch_sides()

    def setRobotKickAbility(self):
        """
        us, they = (self.world.blue_team, self.world.yellow_team) if self.ui.cmbOurTeam.currentText == 'Azul' else (self.world.yellow_team, self.world.blue_team)
        for i in range(self.intelligence.count_robot):
            us[i].can_kick = True if getattr(self.ui, 'kickAbilityU' + str(i)).value > 0.00 else False
            they[i].can_kick = True if getattr(self.ui, 'kickAbilityT' + str(i)).value > 0.00 else False
            print 'Us robot', i, 'ability:', us[i].can_kick
            print 'They robot', i, 'ability', they[i].can_kick

        for r in self.world.robots:
            if r.can_kick == False:
                print 'Robot', r.pattern, 'cannot kick!'
        """
        pass

    def resetPatterns(self):
        if self.useSimulation:
            for i, r in enumerate(self.world.blue_team):
                r.pattern = i
            for i, r in enumerate(self.world.yellow_team):
                r.pattern = i
        else:
            for i, r in enumerate(self.world.blue_team):
                r.pattern = getattr(self.ui, 'cmbRobot_' + str(i)).currentIndex()
            for i, r in enumerate(self.world.yellow_team):
                r.pattern = getattr(self.ui, 'cmbAdversary_' + str(i)).currentIndex()

    def toggleSimulation(self):
        if self.ui.rbtSimulation.isChecked():
            self.intelligence.is_simulation = True
        else:
            self.intelligence.is_simulation = False


    def toggleFullScreen(self):
        if self.ui.windowState() & QtCore.Qt.WindowFullScreen:
            self.ui.showNormal()
            self.ui.dockSetup.show()
            self.ui.dockRobot.show()
            self.ui.menuBar.show()
            #self.ui.statusBar.show()
        else:
            self.ui.showFullScreen()
            self.ui.dockSetup.hide()
            self.ui.dockRobot.hide()
            self.ui.menuBar.show()
            #self.ui.statusBar.hide()
        QtGui.QApplication.processEvents()
        self.ui.stageView.fit()

    def toggleSetupDock(self, activate):
        if activate:
            self.ui.dockSetup.show()
        else:
            self.ui.dockSetup.hide()

    def toggleSetupDockAction(self, activate):
        self.ui.actionSetupDock.setChecked(activate)

    def toggleRobotDock(self, activate):
        if activate:
            self.ui.dockRobot.show()
        else:
            self.ui.dockRobot.hide()

    def toggleRobotDockAction(self, activate):
        self.ui.actionRobotDock.setChecked(activate)

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

        self.stop = False
        self.world = world
        self.count_robot = count_robot
        self.skill = None

        self.mapping_blue = {}
        self.mapping_yellow = {}
        self.kick_mapping_blue = defaultdict(lambda: 100)
        self.kick_mapping_yellow = defaultdict(lambda: 100)

        self.tx_interface = TxInterface(self.world, filters=[], mapping_yellow=self.mapping_yellow, mapping_blue=self.mapping_blue, 
                                        kick_mapping_yellow=self.kick_mapping_yellow, kick_mapping_blue=self.kick_mapping_blue, 
                                        transmission_ipaddr='127.0.0.1', transmission_port=9050)
        self.interface = SimulationInterface(self.world)

        dummy = ('(none)', Dummy())
        self.individual = lambda robot: OrderedDict([
            dummy,
            ('Go To', goto.Goto(robot, target=Point(0, 0))),
            ('Go To Avoid', gotoavoid.GotoAvoid(robot, target=Point(0, 0), avoid=self.world.ball)),
            ('Drive To Object', drivetoobject.DriveToObject(robot, lookpoint=robot.enemy_goal, point=self.world.ball)),
            ('Drive To Ball', drivetoball.DriveToBall(robot, lookpoint=robot.enemy_goal)),
            ('Sampled Dribble', sampleddribble.SampledDribble(robot, lookpoint=robot.enemy_goal)),
            ('Sampled Kick', sampledkick.SampledKick(robot, lookpoint=robot.enemy_goal)),
            ('Follow And Cover', followandcover.FollowAndCover(robot, follow=robot.goal, cover=self.world.ball)),
            ('Sampled Chip Kick', sampledchipkick.SampledChipKick(robot, lookpoint=robot.enemy_goal)),
            ('Kick To (0,0)', kickto.KickTo(robot, lookpoint=Point(0, 0))),
            ('Blocker', blocker.Blocker(robot, arc=0)),
            ('Goalkeeper', goalkeeper.Goalkeeper(robot, angle=30, aggressive=True)),
            ('Zickler43', zickler43.Zickler43(robot)),
            ('Defender', defender.Defender(robot, enemy=self.world.ball)),
            ('Dummy Receive Pass', receivepass.ReceivePass(robot, Point(0,0))),
            ('Joystick', joystick.Joystick(robot)) if joystick is not None else dummy,
        ])
        self.plays = lambda team: OrderedDict([
            dummy,
            ('Auto Retaliate', autoretaliate.AutoRetaliate(team)),
            ('Ifrit', ifrit.Ifrit(team)),
            ('Stop', stop.Stop(team)),
            ('Indirect Kick', indirectkick.IndirectKick(team)),
            ('Obey Referee', obeyreferee.ObeyReferee(autoretaliate.AutoRetaliate(team))),
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

        self.is_simulation = False

    def _loop(self):
        self.current_play_blue.step()
        self.current_play_yellow.step()

        self.current_individual_blue.step()
        self.current_individual_yellow.step()

        with self.world:
            if self.is_simulation:
                self.interface.step()
            else:
                self.tx_interface.step()

    def run(self):
        self.interface.start()
        self.tx_interface.start()
        # FIXME: this catchall catches too many things and breaks debugging
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
            self.tx_interface.stop()


class App(QtGui.QApplication):

    def __init__(self, argv):
        super(App, self).__init__(argv)

        global joystick
        if '--nojoystick' in argv:
            joystick = None

        self.window = QtGraphicalClient()
        self.aboutToQuit.connect(self.window.teardown)
