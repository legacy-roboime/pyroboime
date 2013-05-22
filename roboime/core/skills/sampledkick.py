from .drivetoball import DriveToBall


class SampledKick(DriveToBall):
    """
    This class is a DriveToBall extension that will get the robot
    close to the ball and kick it with enough power to reach a
    given distance with a given speed, that means, arrive at that
    distance with that speed.

    The equation to calculate inital speed is not perfect and may
    need calibration, however one may choose to use the max speed
    instead for most goals.
    """
    # TODO
