from time import time

from ..base import World
#from ..interface.updater import SimVisionUpdater
from ..interface import SimulationInterface
#from ..core.skills import goto
#from ..core.skills import gotoavoid
#from ..core.skills import drivetoobject
#from ..core.skills import drivetoball
#from ..core.skills import sampleddribble
#from ..core.skills import followandcover
#from ..core.skills import sampledchipkick
from ..core.tactics import goalkeeper
from ..core.tactics import blocker
#from ..core.tactics import defender
#from ..core.tactics import zickler43 as zickler
#from ..core.plays import autoretaliate
from ..core.plays import halt
#from ..utils.geom import Point

class Simple(object):
    """
    This is a simple example with no graphical interface.
    """

    def __init__(self, show_fps=False, show_perf=False):
        self.world = World()
        #self.updater = SimVisionUpdater(self.world)
        self.interface = SimulationInterface(self.world)
        self.show_fps = show_fps
        self.show_perf = show_perf
        self.timestamp1 = time()
        self.timestamp2 = time()
        self.skills = {}
        self.tactics = {}
        self.plays = {}
        self.prev_t = time()
        self.frames = 0

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
            r.max_speed = 3.0
            if 'gk' not in self.tactics:
                self.tactics['gk'] = goalkeeper.Goalkeeper(r, angle=30, aggressive=True)
        if 1 in self.world.blue_team:
            r = self.world.blue_team[1]
            r.max_speed = 2.0
            if 'bk' not in self.tactics:
                self.tactics['bk'] = blocker.Blocker(r, arc=0)
                #self.skill = sampledchipkick.SampledChipKick(r, lookpoint=self.world.left_goal)
                #self.skill = followandcover.FollowAndCover(r, follow=self.world.ball, cover=self.world.blue_team[3])
                #self.skill = sampledkick.SampledKick(r, lookpoint=self.world.left_goal)
                #self.skill = sampleddribble.SampledDribble(r, lookpoint=self.world.left_goal)
                #self.skill = drivetoball.DriveToBall(r, lookpoint=self.world.left_goal)
                #self.skill = gotoavoid.GotoAvoid(r, target=Point(0, 0), avoid=self.world.ball)
                #self.skill = goto.Goto(r, target=Point(0, 0))
                #self.skill = goto.Goto(r, x=r.x, y=r.y, angle=90, speed=1, ang_speed=10)
        #if 2 in self.world.yellow_team:
        #    r = self.world.yellow_team[2]
        #    if 'atk' not in self.tactics:
        #        self.tactics['atk'] = zickler.Zickler43(r)
        #        r.max_speed = 2.0
        #if 3 in self.world.blue_team:
        #    r = self.world.blue_team[3]
        #    if 'def' not in self.skills:
        #        self.skills['def'] = defender.Defender(r, enemy=self.world.yellow_team[2])
        #    r.max_speed = 2.0

        #if 'retaliate' not in self.plays:
        #    self.plays['retaliate'] = autoretaliate.AutoRetaliate(self.world.yellow_team, 0)
        if 'halt' not in self.plays:
            self.plays['halt'] = halt.Halt(self.world.yellow_team)

        for p in self.plays.itervalues():
            p.step()
        for t in self.tactics.itervalues():
            t.step()
        for s in self.skills.itervalues():
            s.step()

        t1 = time()
        if self.show_perf:
            print 'heuristic time:', t1 - t0

        #try:
        #    self.interface.step()
        #except:
        ##    pass
        ##finally:
        #    self.interface.stop()
        #else:
        #    self.canvas.draw_field(self.world)
        #t0 = time()
        self.interface.step()
        #t1 = time()
        #print 'inter time:', t1 - t0

        t_diff = t0 - self.prev_t
        if self.show_fps and t_diff >= 1.0:
            frames, self.frames = self.frames / t_diff, 0
            print "fps: {:.02f}".format(frames)
            self.prev_t = t0
        else:
            self.frames += 1

    def mainloop(self):
        self.interface.start()
        self.t0 = time()
        try:
            while True:
                self.loop()
        except KeyboardInterrupt:
            self.interface.stop()
