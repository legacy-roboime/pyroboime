from Tkinter import *
import ttk
from math import pi as PI

from ..base import Field
from ..interface.updater import SimVisionUpdater

FIELD_GREEN = '#3a0'
YELLOW = '#ff0'
BLUE = '#00f'
GREEN = '#0f0'
PINK = '#f0f'
BLACK = '#000'


class FieldCanvas(Canvas):

    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)

        #TODO: make the following dynamic
        self.radius = 0.18
        self.anglespan = 260
        self.field_length = 6.0
        self.field_width = 4.0
        self.field_radius = 0.5
        self.field_margin = 1.0
        self.goal_depth = 0.2
        self.goal_width = 0.7

        self['bg'] = FIELD_GREEN
        self['width'] = 100 * (self.field_length + 2 * self.field_margin)
        self['height'] = 100 * (self.field_width + 2 * self.field_margin)
        self.robots = {}

        # lines
        self.bounds = self.create_rectangle(
            self._cx(-self.field_length / 2),
            self._cy(-self.field_width / 2),
            self._cx(self.field_length / 2),
            self._cy(self.field_width / 2),
            outline='white',
            width=3)
        self.midline = self.create_line(
            self._cx(0),
            self._cy(-self.field_width / 2),
            self._cx(0),
            self._cy(self.field_width / 2),
            fill='white',
            width=3)
        self.center = self.create_oval(
            self._cx(-self.field_radius),
            self._cy(-self.field_radius),
            self._cx(self.field_radius),
            self._cy(self.field_radius),
            outline='white',
            width=3
        )

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
        if self.robots.has_key(id(robot)):
            r = self.robots[id(robot)]
        else:
            r = self.robots[id(robot)] = self.create_arc(
                0, 0, 0, 0,
                outline='',
                style=CHORD,
                extent=self.anglespan)

        self.coords(r,
            self._cx(robot.x - self.radius),
            self._cy(robot.y - self.radius),
            self._cx(robot.x + self.radius),
            self._cy(robot.y + self.radius),
        )
        self.itemconfig(r, start=(robot.angle + 180 - self.anglespan / 2))
        self.itemconfig(r, fill=YELLOW if robot.team.is_yellow else BLUE)


    def delete_robot(self, rid):
        if self.robots.has_key(rid):
            self.delete(self.robots[rid])
            del self.robots[rid]

    def draw_field(self, field):
        # TODO: redraw field size if changed
        # draw all robots on the field
        for r in field.iterrobots():
            self.draw_robot(r)
        # remove missing robots
        rids = map(lambda r: id(r), field.iterrobots())
        for r in self.robots.iterkeys():
            if r not in rids:
                self.delete_robot(r)


class View(Tk):

    def __init__(self):
        Tk.__init__(self)

        self.field = Field()
        self.updater = SimVisionUpdater(self.field)

        self.title('Sample python client.')
        self.resizable(width=False, height=False)#TODO: make this possible
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.content = Frame(self)
        self.content.grid(row=0, column=0, sticky=NSEW)

        self.canvas = FieldCanvas(self.content)
        self.canvas.grid(row=0, column=0, sticky=NSEW)

    def redraw(self):
        self.updater.step()
        self.canvas.draw_field(self.field)
        # how long should we wait?
        self.after(10, self.redraw)

    def mainloop(self):
        self.redraw()
        Tk.mainloop(self)

