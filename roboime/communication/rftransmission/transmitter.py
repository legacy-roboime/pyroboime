class Transmitter(object):
    '''
    Base 'interface' that describes the desired methods for a
    transmitter to be used in our TxCommander. The different
    classes for transmitter manipulation should implement these
    to allow for easy hot-swapping of different transmission modules
    while we do not settle on a new solution.
    '''
    def send(self, array):
        '''
        Sends an array of bytes via radio transmission to the robot.
        '''
        raise NotImplementedError

    def receive(self):
        '''
        Receives an array of bytes from the robot. 
        Not used anywhere as of July/2013.
        '''
        raise NotImplementedError
