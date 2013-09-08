from .goto import Goto


class GotoLooking(Goto):
    def __init__(self, robot, lookpoint=None, **kwargs):
        """
        lookpoint: Where you want it to look, what were you expecting?
        """
        super(GotoLooking, self).__init__(robot, **kwargs)
        self._lookpoint = lookpoint

    @property
    def lookpoint(self):
        if callable(self._lookpoint):
            return self._lookpoint()
        else:
            return self._lookpoint

    @lookpoint.setter
    def lookpoint(self, value):
        self._lookpoint = value

    def _step(self):
        #print self.lookpoint
        self.angle = self.robot.angle_to_point(self.lookpoint)
        super(GotoLooking, self)._step()
