from pathlib import Path
from ruamel.yaml import YAML
import hcl as pyhcl
import json as json_lib
import io


yaml_loader = YAML()


def _data(object):
    if isinstance(object, (io.BufferedIOBase, io.TextIOBase, io.RawIOBase, io.IOBase)):
        return object.read()
    elif isinstance(object, Path):
        return open(object).read()
    else:
        return object


def yaml(input):
    return yaml_loader.load(_data(input))


def hcl(input):
    return pyhcl.loads(_data(input))


def json(input):
    return json_lib.loads(_data(input))


def load_file(filename):
    filename = Path(filename)
    suffix = filename.suffix
    if suffix == '.yaml':
        return yaml(filename)
    elif suffix == '.hcl':
        return hcl(filename)
    elif suffix == '.json':
        return json(filename)
    else:
        raise Exception('Unknown extension {}' % filename)
