#import math
import numpy

_trigonom_ = ['sin', 'cos', 'tan']
_invtrigonom_ = ['a' + f for f in _trigonom_] + ['atan2']
_restricted_ = ['trunc']

for fun in dir(numpy):
    if fun in _restricted_:
        pass
    elif fun in _trigonom_:
        exec '{0} = lambda x: numpy.{0}(numpy.radians(x))'.format(fun) in globals()
    elif fun in _invtrigonom_:
        exec '{0} = lambda x: numpy.degrees(numpy.{0}(x))'.format(fun) in globals()
    else:
        exec '{0} = numpy.{0}'.format(fun)
