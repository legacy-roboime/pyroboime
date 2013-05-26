from time import time

from ..base import World
#from ..interface.updater import SimVisionUpdater
from ..interface import SimulationInterface
from ..core.skills import goto
#from ..core.skills import gotoavoid
#from ..core.skills import drivetoobject
#from ..core.skills import drivetoball
#from ..core.skills import sampleddribble
#from ..core.skills import sampledkick
#from ..core.skills import followandcover
from ..core.skills import sampledchipkick
from ..utils.geom import Point

class Simple(object):
    """
    This is a simple example with no graphical interface.
    """

    def __init__(self, show_fps=False):
        self.world = World()
        #self.updater = SimVisionUpdater(self.world)
        self.interface = SimulationInterface(self.world)
        self.show_fps = show_fps
        self.timestamp1 = time()
        self.timestamp2 = time()
        self.skill = None

    def loop(self):
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
        t0 = time()
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
        t1 = time()
        print 'skill time:', t1 - t0

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
        t0 = time()
        self.interface.step()
        t1 = time()
        print 'inter time:', t1 - t0

        if self.show_fps:
            self.timestamp2, self.timestamp1 = self.timestamp1, time()
            #print "{:.02f}".format(1.0 / (self.timestamp1 - self.timestamp2))
            #print 'step', time() - self.t0

    def mainloop(self):
        self.interface.start()
        self.t0 = time()
        try:
            while True:
                self.loop()
        except KeyboardInterrupt:
            self.interface.stop()
