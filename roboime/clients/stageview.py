#
# Copyright (C) 2013-2015 RoboIME
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
from PyQt4.QtGui import QGraphicsView, QColor, QBrush, QGraphicsScene
from PyQt4.QtCore import Qt

from .qtutils import scale as s
from . import worldviews
from . import skillviews
from . import tacticviews


# colors
FIELD_GREEN = Qt.darkGreen
GREEN = Qt.green
BLUE = Qt.blue
YELLOW = Qt.yellow
BLACK = Qt.black
WHITE = Qt.white
LIGHT_GREY = QColor(0xcc, 0xcc, 0xcc)
ORANGE = QColor(0xff, 0xbb, 0x00)


class StageView(QGraphicsView):
    def __init__(self, parent=None):
        super(StageView, self).__init__(parent)
        self.setBackgroundBrush(QBrush(FIELD_GREEN))
        self.setScene(QGraphicsScene(0, 0, 0, 0))
        self._world = None
        self.scale(1.0 / 15, 1.0 / 15)

        self.ball = None
        self.field = None
        self.robot = []
        self.scene_skills = {}
        self.scene_tactics = {}

    @property
    def world(self):
        return self._world

    @world.setter
    def world(self, w):
        self._world = w
        width, height = s(w.length), s(w.width)
        self.setScene(QGraphicsScene(-1.5 * width, -1.5 * height, 3 * width, 3 * height))

        scene = self.scene()
        self.ball = worldviews.BallView(w.ball)
        scene.addItem(self.ball)
        self.field = worldviews.FieldView(w)
        scene.addItem(self.field)
        for i in xrange(10):
            self.robot.append(worldviews.RobotView(w.blue_team[i]))
            scene.addItem(self.robot[-1])
            self.robot.append(worldviews.RobotView(w.yellow_team[i]))
            scene.addItem(self.robot[-1])

    # Mouse wheel to zoom
    def wheelEvent(self, event):
        scaleFactor = 1.10
        if event.delta() > 0:
            self.scale(scaleFactor, scaleFactor)
        else:
            self.scale(1.0 / scaleFactor, 1.0 / scaleFactor)

    # Resize the view to fit the screen
    def fit(self):
        boundary = self._world.boundary_width + self._world.referee_width
        self.fitInView(
            -s(self._world.length / 2 + boundary),
            -s(self._world.width / 2 + boundary),
            s(self._world.length + 2 * boundary),
            s(self._world.width + 2 * boundary),
            Qt.KeepAspectRatio
        )

    # Handle key events
    def keyPressEvent(self, event):
        # Resets the view
        if event.key() == Qt.Key_Space:
            self.fit()

    def redraw(self):
        scene = self.scene()

        with self.world as w:
            # Update robot skills
            skills = set(map(lambda r: r.skill, w.robots))
            prev_skills = set(self.scene_skills.keys())

            for skill in (skills & prev_skills):
                if not self.scene_skills[skill].isVisible():
                    self.scene_skills[skill].show()

            for skill in (prev_skills - skills):
                if self.scene_skills[skill].isVisible():
                    self.scene_skills[skill].hide()

            for skill in (skills - prev_skills):
                view = skillviews.view_selector(skill)
                if view is not None:
                    scene.addItem(view)
                    self.scene_skills[skill] = view

            # Update robot tactics
            tactics = set(map(lambda r: r.tactic, w.robots))
            prev_tactics = set(self.scene_tactics.keys())

            for tactic in (tactics & prev_tactics):
                if not self.scene_tactics[tactic].isVisible():
                    self.scene_tactics[tactic].show()

            for tactic in (prev_tactics - tactics):
                if self.scene_tactics[tactic].isVisible():
                    self.scene_tactics[tactic].hide()

            for tactic in (tactics - prev_tactics):
                view = tacticviews.view_selector(tactic)
                if view is not None:
                    scene.addItem(view)
                    self.scene_tactics[tactic] = view

            for i in scene.items():
                i.position()

        scene.update()

        '''
        # TODO: only do this when geometry changes
        # clear the old scene
        self.scene().clear()
        self.world = self.world

        # TODO this seems bad, something more performatic is desired
        scene = self.scene()
        scene.clear()

        with self.world as w:
            field = worldviews.FieldView(w)
            field.position()
            scene.addItem(field)

            robots = w.robots

            # bottom layer: the robots
            for r in robots:
                # draw the robot
                robot = worldviews.RobotView(r)
                robot.position()
                scene.addItem(robot)

            # next layer: the robots ids
            for r in robots:
                # draw the robot ids
                robotid = worldviews.RobotIdView(r)
                robotid.position()
                scene.addItem(robotid)

            # next: the ball
            ball = worldviews.BallView(w.ball)
            ball.position()
            scene.addItem(ball)

            # following layers: skills and tactics

            for r in robots:
                # draw the skill
                skill = skillviews.view_selector(r.skill)
                if skill is not None:
                    skill.position()
                    scene.addItem(skill)

            for r in robots:
                # draw the tactic
                tactic = tacticviews.view_selector(r.tactic)
                if tactic is not None:
                    tactic.position()
                    scene.addItem(tactic)
        '''
