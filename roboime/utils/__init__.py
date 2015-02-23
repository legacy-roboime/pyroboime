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


def to_short(x):
    return min(max(x, -32768), 32767)
    # TODO log when it truncates
    #if x == min(max(x, -32768), 32767):
    #    return x
    #else:
    #    raise RuntimeError('THAT ({}) NUMBER IS TOO DAMN HIGH!!!'.format(x))
