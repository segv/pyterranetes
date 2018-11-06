from ruamel.yaml import YAML
from pathlib import Path

yaml_loader = YAML()


def yaml(string):
    return yaml_loader.load(string)


from p10s.engine import Config, value, values  # noqa: F401


__version__ = open(Path(__file__).parent.parent / 'VERSION').read().strip()
