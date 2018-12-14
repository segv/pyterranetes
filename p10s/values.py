from pathlib import Path
from collections import MutableMapping
from copy import deepcopy
from contextlib import contextmanager

from p10s.utils import merge_dicts
from p10s.loads import load_file


class Values(MutableMapping):
    """Class for storing p10s value mappings.

Can be used as a dict. Has classmethods, such as
:py:meth:`p10s.values.Values.from_files` for loading values from
various sources.

    """
    def __init__(self, values=None):
        if values is not None:
            self.values = values
        else:
            self.values = {}

    @classmethod
    def from_files(cls, basedir):
        """Builds a Values object from a hierarchically organzied collections
of yaml files.

All the files named ``values.yaml`` in basedir and up the file system
(up until the file system's root) will be collected and parsed and
merged. The merging is top down, so values specifed in files closer to
basedir will over ride values specified in a higher up values file.

        """
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

    def __getitem__(self, key):
        return self.values[key]

    def __setitem__(self, key, value):
        self.values[key] = value

    def __delitem__(self, key):
        del self.values[key]

    def __iter__(self):
        return iter(self.values)

    def __len__(self):
        return len(self.values)

    def __keytransform__(self, key):
        return key

    def set_value(self, key, value):
        self.values[key] = value

    def get_value(self, key, default=None):
        return self.values.get(key, default)


global VALUES
VALUES = Values()


def use_values(values):
    global VALUES
    VALUES = values


@contextmanager
def values(*args, **kwargs):
    """Run the body with the given key,value pairs bound."""
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
    """Returns the value of the key named ``key``."""
    global VALUES
    return VALUES.get_value(key, default)


def set_value(key, value):
    """Sets the value with the key ``key`` to ``value``."""
    global VALUES
    VALUES.set_value(key, value)
    return value
