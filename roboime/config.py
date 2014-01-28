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
"""
Import this config from this module to get access to the configurations.
To edit your configurations refer to the config/default.yaml there's more
stuff there.
"""
from os import path
import json
import yaml

from .utils.dict_merge import dict_merge

# files to scan
_files = [
    'default.yaml',
    'default.yml',
    'default.json',
    'development.yaml',
    'development.yml',
    'development.json',
    'production.yaml',
    'production.yml',
    'production.json',
]

# default is blank if nothing is found
config = {}
for fname in _files:
    fpath = path.normpath(path.join(path.realpath(path.dirname(__file__)), '..', 'config', fname))
    if path.exists(fpath):
        with open(fpath) as f:
            if fpath.endswith('.yaml') or fpath.endswith('.yml'):
                partial_conf = yaml.load(f)
            elif fpath.endswith('.json'):
                partial_conf = json.load(f)
            config = dict_merge(config, partial_conf)
