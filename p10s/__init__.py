from pathlib import Path


from p10s.engine import Config, value, values  # noqa: F401
from p10s.loads import yaml, json, hcl  # noqa: F401

import p10s.kubernetes as k8s  # noqa: F401
import p10s.terraform as tf  # noqa: F401
import p10s.values  # noqa: F401

__version__ = open(Path(__file__).parent.parent / 'VERSION').read().strip()
