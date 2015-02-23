#
# Copyright (C) 2013-2015 RoboIME
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


class PidController():
    def __init__(self, kp, ki, kd, integ_max, output_max, warn_over_speed=False):
        """ A class to do some PID.

        kp, ki, and kd are proportional, integral and differential constants respectively
        integ_max and output_max are what the name says
        """
        self.kp, self.ki, self.kd = kp, ki, kd
        self.integ_max, self.output_max = integ_max, output_max
        self.error = self.error_prev = self.input = self.feedback = self.output = self.error_int = self.error_dif = 0
        self.warn_over_speed = warn_over_speed

    def step(self):
        self.error = self.input - self.feedback
        self.error_int += self.error

        if self.ki != 0.0:
            self.error_int = max(self.error_int, -abs(self.integ_max / self.ki))
            self.error_int = max(self.error_int, abs(self.integ_max / self.ki))

        self.error_dif = self.error - self.error_prev
        self.error_prev = self.error

        self.output = self.kp * self.error + self.ki * self.error_int + self.kd * self.error_dif

        # output limitation
        self.output = max(self.output, -self.output_max)
        self.output = min(self.output, self.output_max)

        if self.warn_over_speed:
            if self.output == self.output_max:
                print 'WARNING: SPEED LIMIT REACHED'
