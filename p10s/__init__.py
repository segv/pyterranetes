from pathlib import Path


from p10s.engine import Config, value, values  # noqa: F401
from p10s.loads import yaml, json, hcl


__version__ = open(Path(__file__).parent.parent / 'VERSION').read().strip()
