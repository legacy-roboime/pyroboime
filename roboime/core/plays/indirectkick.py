from .stopreferee import StopReferee
from .. import World


class IndirectKick(StopReferee):
    """
    Currently this play will extend StopReferee by performing an
    indirect kick by positioning a robot on a good spot and making
    a pass to it.
    """
    # TODO constructor
    def __init__(self):
    

    def get_best_indirect_position(self, target=enemy_goal, precision=0.5):
        """
        Discretizes points over the field (respecting a minimum border from the field,
        and without entering none of the defense areas), according to given precision.
        Searches for clear paths between initial position (ball), intermediate position,
        and the target.
        
        Returns a sorted tuple of tuples (Points that are closer to the target come 
        first):
        ((point, distance_to_target), (point, distance_to_target), (point, distance_to_target), ...)
        """
        r = self.robot
        # TODO: aim for the best spot in the goal
        b = self.world.ball
        target = self.enemy_goal
        candidate = []
        safety_margin = 2 * r.radius + 0.1
        
        # field params:
        f_l = self.world.field_length - self.world.defense_radius - safety_margin
        f_w = self.world.field_width - safety_margin
        # candidate points in the field range
        for x in range(-f_l/2, f_l/2, precision):
            for y in range(-f_w/2, f_w/2, precision):
                pt = Point(x, y)
                # TODO: 'iterrobots' needs to iterate over the enemies!!!
                for enemy in self.iterrobots():
                    # if the robot -> pt line doesn't cross any enemy body...
                    if not Line(b, pt).crosses(enemy.body):
                        final_line = Line(pt, target)
                        # if the pt -> target line doesn't cross any enemy body...
                        if not final_line.crosses(enemy.body):
                            # this is a candidate point!
                            candidate.append((pt, final_line.length))
        candidate = sorted(candidate, key=lambda tup: tup[1])
        # candidate[0][0] will be the best position
        return candidate