from dataclasses import dataclass
from pathlib import Path
import sys
from ruamel.yaml import YAML
import json
from pprint import pprint
import runpy
from contextlib import contextmanager

global Values
Values = {}


@contextmanager
def values(**kwargs):
    global Values
    old = Values
    new = old.copy()
    for k, v in kwargs.items():
        new[k] = v
    Values = new
    yield
    Values = old


def value(key, *args):
    global Values
    args = list(args)

    if len(args) > 0:
        return Values.get(key, args[0])
    else:
        if key in Values:
            return Values[key]
        else:
            raise ValueError(f'Key {key} not found in {Values}')


def set_value(key, value):
    global Values
    Values[key] = value


yaml = YAML()
yaml.default_flow_style = False


class Config():
    def __init__(self, data=None):
        self.data = data

    @staticmethod
    def merge(a, b, path=None):
        "merges b into a"
        if path is None:
            path = []
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    Config.merge(a[key], b[key], path + [str(key)])
                else:
                    a[key] = b[key]
            else:
                a[key] = b[key]
        return a

    def set(self, values):
        self.data = Config.merge(self.data, values)
        return self

    def serialize(self):
        def _serialize(thing):
            if isinstance(thing, dict):
                raw = {k: _serialize(v) for k, v in thing.items()}
            elif isinstance(thing, (list, tuple)):
                raw = [_serialize(v) for v in thing]
            elif isinstance(thing, Config):
                raw = thing.serialize()
            elif isinstance(thing, Path):
                raw = str(thing)
            else:
                raw = thing

            return raw

        return _serialize(self.data)

    def generate(self, output=None, format='yaml'):
        data = self.serialize()

        if format == 'pprint':
            pprint(data)
        elif format == 'yaml':
            yaml.dump(data, sys.stdout)
        elif format == 'json':
            print(json.dump(data))


class EngineException(Exception):
    pass


@dataclass
class SourceDoesNotExist(EngineException):
    source: Path


class Compiler():
    def __init__(self, filename):
        self.filename = Path(filename)

    def compile(self, output=None):
        if not self.filename.exists():
            raise SourceDoesNotExist(self.filename)

        lib = self.filename.resolve().parent

        while True:
            maybe = lib / 'conf_obj'
            if maybe.exists() and maybe.is_dir():
                lib = maybe
                break
            if maybe == maybe.root:
                lib = None
                break
            lib = lib.parent

        if lib:
            sys.path.insert(0, f'{lib}/')

        with values(__file__=self.filename,
                    __output__=output):
            runpy.run_path(str(self.filename))
