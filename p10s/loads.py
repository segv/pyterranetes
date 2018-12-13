from pathlib import Path
from ruamel.yaml import YAML
import hcl as pyhcl
import json as json_lib
import io


ruamel = YAML(typ='safe', pure=True)
ruamel.default_flow_style = False


def _data(object):
    if isinstance(object, (io.BufferedIOBase, io.TextIOBase, io.RawIOBase, io.IOBase)):
        return object.read()
    elif isinstance(object, Path):
        return object.open().read()
    else:
        return object


def yaml(input):
    try:
        return ruamel.load(_data(input))
    except Exception as e:
        print("Error parsing %s" % input)
        raise(e)


def yaml_all(input):
    try:
        return ruamel.load_all(_data(input))
    except Exception as e:
        print("Error parsing %s" % input)
        raise(e)


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
