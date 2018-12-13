from pathlib import Path
from p10s.utils import merge_dicts
from p10s.loads import load_file
from contextlib import contextmanager
from copy import deepcopy


class Values():
    def __init__(self, values=None):
        if values is not None:
            self.values = values
        else:
            self.values = {}

    @classmethod
    def from_files(cls, basedir):
        basedir = Path(basedir)
        if not basedir.exists():
            raise Exception("basedir {} does not exist" % basedir)
        root = basedir.resolve().root
        here = basedir

        values_files = []

        while str(here) != root:
            if (here / 'values.yaml').exists():
                values_files.insert(0, here / 'values.yaml')
            here = here.parent

        values = {}
        for file in values_files:
            merge_dicts(values, load_file(file))

        return cls(values)

    def copy(self):
        return Values(values=deepcopy(self.values))

    def set_value(self, key, value):
        self.values[key] = value

    def get_value(self, key, default=None):
        return self.values.get(key, default)


global VALUES
VALUES = Values()


@contextmanager
def values(*args, **kwargs):
    global VALUES
    old = VALUES
    new = old.copy()
    for d in args:
        for k, v in d.items():
            new.set_value(k, v)
    for k, v in kwargs.items():
        new.set_value(k, v)
    VALUES = new
    yield
    VALUES = old


def value(key, default=None):
    global VALUES
    return VALUES.get_value(key, default)


def set_value(key, value):
    global VALUES
    VALUES.set_value(key, value)
    return value
