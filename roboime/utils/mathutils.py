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
import numpy as np
from numpy import math

_trigonom_ = ['sin', 'cos', 'tan']
_invtrigonom_ = ['a' + f for f in _trigonom_] + ['atan2']
_restricted_ = ['trunc']

for fun in dir(math):
    if fun in _restricted_:
        pass
    elif fun in _trigonom_:
        exec('{0} = lambda x: math.{0}(math.radians(x))'.format(fun), globals())
    elif fun == 'atan2':
        exec('{0} = lambda y, x: math.degrees(math.{0}(y, x))'.format(fun), globals())
    elif fun in _invtrigonom_:
        exec('{0} = lambda x: math.degrees(math.{0}(x))'.format(fun), globals())
    else:
        exec('{0} = math.{0}'.format(fun))


def norm(vector):
    """ Returns the norm (length) of the vector."""
    # note: this is a very hot function, hence the odd optimization
    # Unoptimized it is: return np.sqrt(np.sum(np.square(vector)))
    return np.sqrt(np.dot(vector, vector))


def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / norm(vector)


def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    angle = np.arccos(np.dot(v1_u, v2_u))
    if math.isnan(angle):
        if (v1_u == v2_u).all():
            return 0.0
        else:
            return 180
    return math.degrees(angle)
