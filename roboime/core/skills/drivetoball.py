from numpy import remainder

from .drivetoobject import DriveToObject


class DriveToBall(DriveToObject):
    """
    This skill is a DriveToObject except that the object is the ball
    and that some parameters are optimized for getting on the ball.
    """

    attraction_factor = 70
    #magnetic_factor = 0.1
    def __init__(self, robot, **kwargs):
        # TODO: magic parameters
        super(DriveToBall, self).__init__(robot, point=robot.world.ball, **kwargs)
        self.avoid = robot.world.ball

    def _step(self):
        if self.target is not None and self.lookpoint is not None:
            base_angle = self.target.angle_to_point(self.ball)
            robot_angle = self.robot.angle_to_point(self.ball)
            delta = remainder(robot_angle - base_angle, 360)
            delta = min(abs(delta), abs(delta - 360))
            if delta >= 45:
                self.should_avoid = True

            if self.should_avoid:
                if delta <= 30:
                    self.should_avoid = False

        super(DriveToBall, self)._step()
