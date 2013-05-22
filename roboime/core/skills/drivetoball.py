from .drivetoobject import DriveToObject


class DriveToBall(DriveToObject):
    """
    This skill is a DriveToObject except that the object is the ball
    and that some parameters are optimized for getting on the ball.
    """
    def __init__(self, robot, **kwargs):
        # TODO: magic parameters
        super(DriveToBall, self).__init__(robot, point=robot.world.ball, **kwargs)
