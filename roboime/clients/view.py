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
from Tkinter import Canvas, Frame, Tk, CHORD, NSEW
from time import time

from ..base import World, Blue, Yellow
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
#from ..utils.geom import Point

FIELD_GREEN = '#3a0'
YELLOW = '#ff0'
BLUE = '#00f'
GREEN = '#0f0'
PINK = '#f0f'
BLACK = '#000'
ORANGE = '#f80'
WHITE = '#FFF'


class FieldCanvas(Canvas):

    def __init__(self, *args, **kwargs):
        self.world = kwargs["world"]
        del kwargs["world"]

        Canvas.__init__(self, *args, **kwargs)

        #TODO: make the following dynamic
        self.anglespan = 260
        self.field_length = 6.0
        self.field_width = 4.0
        self.field_radius = 0.5
        self.field_margin = 1.0
        self.goal_depth = 0.2
        self.goal_width = 0.7
        self.thickness = 1
        self.has_field = False

        self['bg'] = FIELD_GREEN
        self['width'] = 100 * (self.field_length + 2 * self.field_margin)
        self['height'] = 100 * (self.field_width + 2 * self.field_margin)
        self.robots = {}
        self.balls = {}

        self.fps = self.create_text(50, 20, fill=BLACK)

    def _cx(self, x):
        'Convert internal x coord to canvas x coord'
        return 100 * (self.field_length / 2 + self.field_margin + x)

    def _cy(self, y):
        'Convert internal x coord to canvas x coord'
        return 100 * (self.field_width / 2 + self.field_margin - y)

    def _cc(self, x, y):
        'Convert to canvas coords.'
        return (self._cx(x), self._cy(y))

    def draw_robot(self, robot):
        if id(robot) in self.robots:
            r = self.robots[id(robot)]
        else:
            r = self.robots[id(robot)] = self.create_arc(
                0, 0, 0, 0,
                outline='',
                style=CHORD,
                extent=self.anglespan)

        self.coords(
            r,
            self._cx(robot.x - robot.radius),
            self._cy(robot.y - robot.radius),
            self._cx(robot.x + robot.radius),
            self._cy(robot.y + robot.radius),
        )
        self.itemconfig(r, start=(robot.angle + 180 - self.anglespan / 2))
        if robot is self.world.closest_robot_to_ball():
            self.itemconfig(r, outline=BLACK)
        else:
            self.itemconfig(r, outline=FIELD_GREEN)
        if not self.world.is_in_defense_area(robot):
            self.itemconfig(r, fill=YELLOW if robot.team.is_yellow else BLUE)
        else:
            self.itemconfig(r, fill=GREEN if robot.team.is_yellow else PINK)

    def draw_ball(self, ball):
        if id(ball) in self.balls:
            b = self.balls[id(ball)]
        else:
            b = self.balls[id(ball)] = self.create_oval(
                0, 0, 0, 0,
                outline='')

        self.coords(
            b,
            self._cx(ball.x - ball.radius),
            self._cy(ball.y - ball.radius),
            self._cx(ball.x + ball.radius),
            self._cy(ball.y + ball.radius),
        )
        self.itemconfig(b, fill=ORANGE)

    def delete_robot(self, rid):
        if rid in self.robots:
            self.delete(self.robots[rid])
            del self.robots[rid]

    def create_field(self, world):
        # lines
        self.bounds = self.create_rectangle(
            self._cx(-world.length / 2),
            self._cy(-world.width / 2),
            self._cx(world.length / 2),
            self._cy(world.width / 2),
            outline='white',
            width=self.thickness,
        )
        self.midline = self.create_line(
            self._cx(0),
            self._cy(-world.width / 2),
            self._cx(0),
            self._cy(world.width / 2),
            fill='white',
            width=self.thickness,
        )
        self.center = self.create_oval(
            self._cx(-world.center_radius),
            self._cy(-world.center_radius),
            self._cx(world.center_radius),
            self._cy(world.center_radius),
            outline='white',
            width=self.thickness,
        )

        for color in [Blue, Yellow]:
            self.draw_defense_area(world.defense_area(color))

        for goal in [world.left_goal, world.right_goal]:
            self.draw_goal(goal)

        self.has_field = True

    def draw_field(self, world):
        # TODO: redraw field size if changed
        if not self.has_field:
            if world.inited:
                self.create_field(world)

        if self.has_field:
            self.draw_ball(world.ball)
            # draw all robots on the field
            for r in world.iterrobots():
                self.draw_robot(r)
            # remove missing robots
            rids = map(id, self.world.iterrobots())
            for r in self.robots.iterkeys():
                if r not in rids:
                    self.delete_robot(r)

    def draw_defense_area(self, defense_area):
        converted_polygon = [(self._cx(x), self._cy(y)) for (x, y) in defense_area.exterior.coords]
        self.create_polygon(converted_polygon,
                            outline=WHITE,
                            fill='')

    def draw_goal(self, goal):
        converted_polygon = [(self._cx(x), self._cy(y)) for (x, y) in goal.body.coords]
        self.create_polygon(converted_polygon,
                            outline=WHITE,
                            fill='')

    def draw_fps(self, text):
        self.itemconfig(self.fps, text=str(text))


class View(Tk):

    def __init__(self):
        Tk.__init__(self)

        self.world = World()
        #self.updater = SimVisionUpdater(self.world)
        self.interface = SimulationInterface(self.world)

        self.title('Sample python client.')
        # TODO: make this possible
        self.resizable(width=False, height=False)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.content = Frame(self)
        self.content.grid(row=0, column=0, sticky=NSEW)

        self.canvas = FieldCanvas(self.content, world=self.world)
        self.canvas.grid(row=0, column=0, sticky=NSEW)

        self.timestamp1 = time()
        self.timestamp2 = time()

    def redraw(self):
        #print "I'm in!"
        #if len(self.world.blue_team) > 0:
        #if 0 in self.world.blue_team:
        #    r = self.world.blue_team[0]
        #    #import pudb; pudb.set_trace()
        #    #print 'hey'
        #    a = r.action
        #    a.x = 0.0
        #    a.y = 0.0
        #    a.angle = 0.0
        #if 1 in self.world.blue_team:
        #    r = self.world.blue_team[1]
        #    r.action.speeds = (1.0, 0.0, 0.0)
        #pdb.set_trace()
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

        #try:
        #    self.interface.step()
        #except:
        ##    pass
        ##finally:
        #    self.interface.stop()
        #else:
        #    self.canvas.draw_field(self.world)
        #    # how long should we wait?
        #    self.after(10, self.redraw)
        #pdb.set_trace()
        self.interface.step()
        #pdb.set_trace()
        self.canvas.draw_field(self.world)
        # how long should we wait?
        self.timestamp2, self.timestamp1 = self.timestamp1, time()
        self.canvas.draw_fps("{:.02f}".format(1.0 / (self.timestamp1 - self.timestamp2)))
        #self.after(10, self.redraw)
        #print "Redrawing in a few"
        self.after(1, self.redraw)

    def mainloop(self):
        self.skill = None
        self.interface.start()
        self.redraw()
        Tk.mainloop(self)
        self.interface.stop()
