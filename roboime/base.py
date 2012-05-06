

class Robot:
    """
    This class represents a robot, regardless of the team.
    A robot doesn't 
    """

    def __init__(self):
        # identification
        self.id = None
        self.pattern = None
        self.color = None
        # components
        self.dribbler = None
        self.kicker = None
        self.wheels = [None] * 4
        self.battery = None
