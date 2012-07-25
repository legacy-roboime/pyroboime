from Tkinter import *
import ttk

FIELD_GREEN = '#3a0'
YELLOW = '#ff0'
BLUE = '#00f'
GREEN = '#0f0'
PINK = '#f0f'
BLACK = '#000'


class FieldCanvas(Canvas):

    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self['bg'] = FIELD_GREEN
        self['height'] = self._cc(FIELD_WIDTH + 2 * FIELD_MARGIN)
        self['width'] = self._cc(FIELD_LENGTH + 2 * FIELD_MARGIN)
        self.robots = {}

        #TODO: make the following dynamic
        self.radius = 0.18
        self.anglespan = 260
        self.field_length = 6.0
        self.field_width = 4.0
        self.field_radius = 0.5
        self.field_margin = 1.0
        self.goal_depth = 0.2
        self.goal_width = 0.7

        # lines
        boundx1, boundy1 = self._cc(FIELD_MARGIN, FIELD_MARGIN)
        self.bounds = self.create_rectangle(
            boundx1,
            boundy1,
            _cc(FIELD_MARGIN + FIELD_LENGTH),
            _cc(FIELD_MARGIN + FIELD_WIDTH),
            outline='white',
            width=3)
        self.midline = self.create_line(
            _cc(FIELD_MARGIN + FIELD_LENGTH / 2),
            _cc(FIELD_MARGIN),
            _cc(FIELD_MARGIN + FIELD_LENGTH / 2),
            _cc(FIELD_MARGIN + FIELD_WIDTH),
            outline='white',
            width=3)


    def _cc(self, x, y):
        "Convert to canvas coords."
        return map(lambda i: i * 100, (FIELD_LENGTH / 2 + FIELD_MARGIN + x, FIELD_WIDTH / 2 + FIELD_MARGIN - y))

    def draw_robot(self, robot):
        if not self.robots.has_key(id(robot)):
            r = self.robots[robot.uid] = self.create_arc(
                0, 0, 0, 0,
                outline='',
                style=CHORD,
                extent=ANGLESPAN)
        else:
            r = self.robots[id(robot)]

        x1, y1 = self._cc(robot.x - RADIUS, robot.y - RADIUS)
        x2, y2 = self._cc(robot.x + RADIUS, robot.y + RADIUS)
        sa = robot.angle + 180 - ANGLESPAN / 2

        self.coords(r, x1, y1, x2, y2)
        self.itemconfig(r, start=sa)
        self.itemconfig(r, state=NORMAL)
        self.itemconfig(r, fill=YELLOW if robot.team.is_yellow else BLUE)


    def delete_robot(self, robot):
        if self.robots.has_key(robot.uid):
            self.delete(self.robots[robot.uid])

    def hide_robot(self, robot):
        if self.robots.has_key(robot.uid):
            self.itemconfig(self.robots[robot.uid], state=HIDDEN)


class View(Tk):

    def __init__(self):
        Tk.__init__(self)

        self.title('Sample python client.')
        self.resizable(width=False, height=False)#TODO: make this possible
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.content = Frame(self)
        self.content.grid(row=0, column=0, sticky=NSEW)

        self.canvas = FieldCanvas(self.content)
        self.canvas.grid(row=0, column=0, sticky=NSEW)

