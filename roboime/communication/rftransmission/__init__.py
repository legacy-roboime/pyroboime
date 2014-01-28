#
# Copyright (C) 2013 RoboIME
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
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
