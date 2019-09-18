"""Generating config files.

Very often we need to generate a few files of yaml, or json, or ini
encoded data.

.. code-block:: python

    from p10s import cfg

    setup = cfg.JSONContext("config.json")
    setup += {"VAR": "VALUE"}

    c.variable.name = 'default-value'

"""
import configparser
import json
from copy import deepcopy

from p10s.base import BaseContext
from p10s.loads import ruamel
from p10s.utils import merge_dicts


class ConfigContext(BaseContext):
    def __init__(self, *args, data=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = data if data is not None else {}

    def add(self, data):
        self.data = merge_dicts(self.data, data)
        return self

    def __iadd__(self, data):
        return self.add(data)

    def __add__(self, data):
        return deepcopy(self).add(data)


class INIContext(ConfigContext):
    """Context for ini files.

    Does not support the full nested sections allowed by configparser,
    one level deep only, and values must be scalars.

    """

    output_file_extension = ".ini"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configparser = configparser.ConfigParser()

    def add(self, data):
        for key, value in data.items():
            self.configparser[key] = value
        return self

    def render_to_stream(self, stream):
        self.configparser.write(stream)


class YAMLContext(ConfigContext):
    """Context for yaml files."""

    output_file_extension = ".yaml"

    def render_to_stream(self, stream):
        ruamel.dump_all([self.data], stream)


class JSONContext(ConfigContext):
    """Context for json files."""

    output_file_extension = ".json"

    def render_to_stream(self, steam):
        json.dump(self.data, steam, indent=4, sort_keys=True)
