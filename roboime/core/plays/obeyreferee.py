from numpy.linalg import norm

from .. import Play
from ..stopreferee import StopReferee
from ..stop import Stop
from ..halt import Halt
from ..penalty import Penalty
from ..penaltydefend import PenaltyDefend
from ..indirectkick import IndirectKick
from ..base import Referee, Blue, Yellow
from ..utils.geom import Point, Line


class ObeyReferee(Play):
    """
    Sometimes we should obey the referee, this class will do it
    and also switch the appropriate plays for each ocasion.
    """
    Command = Referee.Command
    TOLERANCE = 0.05

    def __init__(self, play, goalkeeper_uid, penalty_kicker, verbose=False):
        super(ObeyReferee, self).__init__(play.team)
        self.play = play
        self.stop = Stop(self.team, goalkeeper_uid)
        self.halt = Halt(self.team)
        self.penalty_us = Penalty(self.team, goalkeeper_uid)
        self.penalty_them = PenaltyDefend(self.team, goalkeeper_uid)
        self.indirect_kick = IndirectKick(self.team, goalkeeper_uid)
        self.referee = self.world.referee
        self.command = Command.Halt
        self.last_command = Command.Halt
        self.last_ball = Point(self.world.ball)
        self.verbose = verbose

    def step(self):
        first_time = False
        ball_distance = ball.distance(last_ball) 
        if self.command != self.referee.command:
            self.last_command = self.command
            self.command = self.referee.command
            self.last_ball = Point(Ball)
            first_time = True

       if verbose:
            print 'JUIZ ', self.command

        if (self.command == Command.DirectFreeYellow and self.team.color == Yellow)
                or (self.command == Command.DirectFreeBlue and self.team.color == Blue):
            self.play.step()

        elif (self.command == Command.PreparePenaltyYellow and self.team.color == Yellow)
                or (self.command == Command.PreparePenaltyBlue and self.team.color == Blue): 
            # Sets up the penalty kicker on the penalty position
            self.penalty_us.step()


        elif self.command == Command.NormalStart and 
                ((self.last_command == Command.PreparePenaltyYellow and self.team.color == Yellow) or
                (self.last_command == Command.PreparePenaltyBlue and self.team.color == Blue)):
            # After the penalty kicker reaches its position, it actually kicks
            self.penalty_us.ready = True
            self.penalty_us.step()

            if penalty_us.attacker.is_last_toucher:
                self.last_command = Command.NormalStart
        
        elif (self.command == Command.PreparePenaltyYellow and self.team.color == Blue) or
                 (self.command == Command.PreparePenaltyBlue and self.team.color == Yellow):
            self.penalty_them.step()

        elif (self.last_command == Command.PreparePenaltyYellow and self.team.color == Blue) or
                (self.last_command == Command.PreparePenaltyBlue and self.team.color == Yellow):
            if norm(self.worldball.speed) > TOLERANCE or distance > TOLERANCE:
                self.play.step()
                self.last_command = Command.NormalStart
            else:
                self.penalty_them.step()

        elif (self.command == Command.DirectFreeBlue and self.team.color == Yellow) or
                (self.command == Command.DirectFreeYellow and self.team.color == Blue) or
                (self.command == Command.IndirectFreeBlue and self.team.color == Yellow) or
                (self.command == Command.IndirectFreeYellow and self.team.color == Blue) or
                (self.command == Command.NormalStart and 
                (self.last_command == Command.PrepareKickoffYellow and self.team.color == Blue) or
                (self.last_command == Command.PrepareKickoffBlue and self.team.color == Yellow)):
            if norm(self.worldball.speed) > TOLERANCE or distance > TOLERANCE:
                self.play.step()
            else:
                self.stop.step()

        elif (self.command == Command.IndirectFreeBlue and self.team.color == Blue) or
                (self.command == Command.IndirectFreeYellow and self.team.color == Yellow):
            if first_time:
                self.indirect_kick.restart()
            if self.indirect_kick.current_state == self.indirect_kick.states['end']:
                self.play.step()
            else:
                self.indirect_kick.step()
        
        elif self.command in [Command.PrepareKickoffYellow, Command.PrepareKickoffBlue]:
            self.stop.step()

        elif self.command == Command.NormalStart and 
                ((self.last_command == Command.PrepareKickoffYellow and self.team.color == Yellow) or
                (self.last_command == Command.PrepareKickoffBlue and self.team.color == Blue)):
            self.play.step()
        
        else:
            self.play.step()
 

