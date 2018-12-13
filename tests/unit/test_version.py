from p10s import __version__
from pathlib import Path


def test_version():
    assert __version__ == open(Path(__file__).parent.parent.parent / 'VERSION').read().strip()
