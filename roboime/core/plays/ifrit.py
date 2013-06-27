from numpy import array, sign

from .. import Play
from ..tactics.goalkeeper import Goalkeeper
from ..tactics.zickler43 import Zickler43
from ..tactics.blocker import Blocker
from ..tactics.defender import Defender
from ..tactics.executepass import ExecutePass
from ..tactics.receivepass import ReceivePass
from ..tactics.receivepassandkick import ReceivePassAndKick
from ...utils.mathutils import angle_between
from ...utils.geom import Point, Line

from numpy import linspace

class Ifrit(Play):
    """
    This is the first cooperative play in this project.

    Basically, set the closest robot to the ball to be either an attacker
    - in case he has a clear shot to the goal - or a passer, if he does not.

    We'll have a second robot in a receiving position: a pivot, which will
    be ready to receive the ball and immediately kick it towards the goal. 

    The rest is the same as the autoretaliate play.
    """

    def __init__(self, team, **kwargs):
        """
        team: duh
        """
        super(Ifrit, self).__init__(team, **kwargs)
        self.players = {}
        self.last_passer = None
        self.tactics_factory.update({
            'goalkeeper': lambda robot: Goalkeeper(robot, aggressive=False, angle=0),
            'attacker': lambda robot: Zickler43(robot),
            'blocker': lambda robot: Blocker(robot, arc=0),
            'defender': lambda robot: Defender(robot, enemy=self.ball, distance=0.6),
            'passer': lambda robot: ExecutePass(robot),
            'receiver': lambda robot: ReceivePassAndKick(robot),
        })

    def setup_tactics(self):
        # Make sure that the robot receiving the ball keeps kicking it even if its tactic changes.
        for attacker in [self.players[x.uid]['attacker'] for x in self.team]:
            if attacker.time_of_last_kick + .5 < self.world.timestamp:
                self.hold_down_passer = self.last_passer
            if attacker.time_of_last_kick + 8 < self.world.timestamp and self.last_passer is not None:
                #print self.hold_down_passer.uid
                self.hold_down_passer.action.kick = 1

        # list of the ids of the robots in order of proximity to the ball
        closest_robots = [r.uid for r in self.team.closest_robots_to_ball(can_kick=True)]
        # make sure we do not account for the goalkeeper on that list
        gk_id = self.goalie
        if gk_id in closest_robots:
            closest_robots.remove(gk_id)

        atk_id = closest_robots[0] if len(closest_robots) > 0 else None


        # Here we split from autoretaliate.         
        # We'll find now the best position for our pivot to receive a possible pass.
        best_position = self.best_receiver_positions(self.team[atk_id], self.last_passer)[0][0]
        robots_closest_to_bathtub = self.team.closest_robots_to_point(point=best_position)
        if self.team[atk_id] in robots_closest_to_bathtub:
            robots_closest_to_bathtub.remove(self.team[atk_id])
        if self.team[gk_id] in robots_closest_to_bathtub:
            robots_closest_to_bathtub.remove(self.team[gk_id])
        
        # Here, we'll get a pivot.
        pvt_id = robots_closest_to_bathtub[0].uid if len(robots_closest_to_bathtub) > 0 else None
        if pvt_id in closest_robots: 
            closest_robots.remove(pvt_id)
        
        blk_id = closest_robots[1] if len(closest_robots) > 1 else None

        # gather the defenders (not goalkeeper, attacker, pivot or blocker)
        defenders = [r for r in self.team if r.uid not in [gk_id, atk_id, blk_id, pvt_id]]

        # iterate over list of enemies by proximity to the goal
        for enemy in self.enemy_team.closest_robots_to_point(self.team.goal):
            # if there are free defenders, assign the closest to the enemy, to follow it
            if len(defenders) > 0:
                defender = enemy.closest_to(defenders)
                defenders.remove(defender)
                self.players[defender.uid]['defender'].enemy = enemy
        
        # for any remaining defender, let them guard the ball
        for defender in defenders:
            self.players[defender.uid]['defender'].enemy = self.ball

        # Setting position for the pivot 
        if pvt_id is not None:
            self.players[pvt_id]['receiver'].point = best_position
        goal_kick = True 
        # Check if we want to pass or if we want to kick.
        if atk_id is not None and pvt_id is not None:
            if self.world.has_clear_shot(self.players[atk_id]['attacker'].lookpoint):
                goal_kick = True
                self.players[pvt_id]['receiver'].companion = self.players[atk_id]['attacker']
            #print self.players[pvt_id]['receiver'].companion, self.players[atk_id]['attacker']
            else:
                self.players[atk_id]['passer'].companion = self.players[pvt_id]['receiver']
                self.players[pvt_id]['receiver'].companion = self.players[atk_id]['passer']
                goal_kick = False
        #print self.is_valid_position(self.team[0], self.team[1], verbose=True)
        # step'em, this is needed to guarantee we're only stepping active robots
        for robot in self.team:
            r_id = robot.uid
            if r_id == gk_id:
                robot.current_tactic = self.players[r_id]['goalkeeper']
            elif r_id == atk_id and goal_kick:
                robot.current_tactic = self.players[r_id]['attacker']
            elif r_id == atk_id and not goal_kick:
                robot.current_tactic = self.players[r_id]['passer']
                
                self.last_passer = robot
            elif r_id == blk_id:
                robot.current_tactic = self.players[r_id]['blocker']
            elif r_id == pvt_id:
                robot.current_tactic = self.players[r_id]['receiver']
            else:
                robot.current_tactic = self.players[r_id]['defender']

        #print self.is_valid_position(self.players[pvt_id]['receiver'].point, self.team[atk_id], verbose=True)

    def is_valid_position(self, point, passer, verbose=False):
        base_array = array(point) - array(self.world.ball)
        p0, p1 = array(passer.enemy_goal.p1) - array(point), array(passer.enemy_goal.p2) - array(point)
        angle1, angle2 = angle_between(base_array, p0), angle_between(base_array, p1)
        for angle in [angle1, angle2]:
            angle = angle if angle < 180 else angle - 360
        if verbose:
            print angle1, angle2
        return abs(angle1) < 70 and abs(angle2) < 70 and (not Line(point, passer.enemy_goal.p1).crosses(passer.body)) and (not Line(point, passer.enemy_goal.p2).crosses(passer.body))
    
    def best_receiver_positions(self, passer, current_position, target=None, precision=6):
        """
        Discretizes points over the field (respecting a minimum border from the field,
        and without entering none of the defense areas), according to given precision.
        Searches for clear paths between initial position (ball), intermediate position,
        and the target.

        Returns a sorted list of tuples (Points that are closer to the target come
        first):
        [(point, distance_to_target), (point, distance_to_target), (point, distance_to_target), ...]
        """
        # TODO: aim for the best spot in the goal, not only to the middle of the enemy goal

        #t = self.team
        b = self.world.ball

        if target is None:
            #target = self.team.enemy_goal
            target = self.team.enemy_goal

        candidate = []
        candidate_no_vision = []
        safety_margin = 2 * self.team[0].radius + 0.1

        # field params:
        f_l = self.world.length - self.world.defense_radius - safety_margin
        f_w = self.world.width - safety_margin

        # candidate points in the field range
        for x in linspace(-f_l / 2, f_l / 2, precision):
            for y in linspace(-f_w / 2, f_w / 2, precision - 2):
                pt = Point(x, y)
                if not self.is_valid_position(pt, passer):
                    acceptable = False
                else:
                    acceptable = True
                final_line = Point(0, 0)
                for enemy in self.team.enemy_team.iterrobots():
                    # if the robot -> pt line doesn't cross any enemy body...
                    start_line = Line(b, pt)
                    if start_line is not None and not start_line.crosses(enemy.body):
                        final_line = Line(pt, target)
                        # if the pt -> target line crosses any enemy body...
                        if final_line.crosses(enemy.body):
                            acceptable = False
                if acceptable:
                    if current_position is not None:
                        candidate += [(pt, pt.distance(current_position))]
                    else:
                        candidate += [(pt, 0)]
        if not candidate and current_position is not None:
            #goal_point = self.enemy_goal
            return [(Point(current_position), 0)]
        elif current_position is None:
            return [(Point(self.team.goal.x - sign(self.team.goal.x)*1.5,self.team.goal.y - 1), 0)]
        else:
            return sorted(candidate, key=lambda tup: tup[1])    

