# encoding: utf-8
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
"""
General options during execution
"""

#Position Log filename. Use None to disable.
position_log_filename = "math/pos_log.txt"
#position_log_filename = None

#Command and Update Log filename. Use None to disable.
cmdupd_filename = "math/commands.txt"
#cmdupd_filename = None

#Gaussian noise addition variances
noise_var_x = 3.E-5
noise_var_y = 3.E-5
noise_var_angle = 1.

# Process error estimate. The lower (higher negative exponent), more the filter
# becomes like a Low-Pass Filter (higher confidence in the model prediction).
Q = 1e-5

# Measurement error variances (for the R matrix).
# The higher (lower negative exponent), more the filter becomes like a
# Low-Pass Filter (higher possible measurement error).
R_var_x = 3.E-5
R_var_y = 3.E-5
R_var_angle = 1e-5
