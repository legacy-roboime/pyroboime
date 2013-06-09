from .. import Play
from ..stopreferee import StopReferee


class ObeyReferee(Play):
    """
    Sometimes we should obey the referee, this class will do it
    and also switch the appropriate plays for each ocasion.
    """
    def __init__(self, play, goalkeeper, penalty_kicker):
        super(ObeyReferee, self).__init__(play.team)
        self.play = play
        self.stop = Stop(self.play.team, goalkeeper.uid)
        self.halt = Halt(self.play.team)
        #TODO

    def step(self):
        raise NotImplementedError
