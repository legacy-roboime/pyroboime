from os import path

import yaml

from .utils.dict_merge import dict_merge

# files to scan
_files = [
    'default.yaml',
    'development.yaml',
    'production.yaml',
]

# default is blank if nothing is found
config = {}
for fname in _files:
    fpath = path.normpath(path.join(path.realpath(path.dirname(__file__)), '..', 'config', fname))
    if path.exists(fpath):
        with open(fpath) as f:
            if fpath.endswith('.yaml') or fpath.endswith('.yml'):
                partial_conf = yaml.load(f)
            config = dict_merge(config, partial_conf)
