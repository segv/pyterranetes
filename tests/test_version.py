from p10s import __version__
from pathlib import Path
import runpy


def test_version():
    g = runpy.run_path(str(Path(__file__).parent.parent / 'p10s' / '__version__.py'))
    assert __version__ == g['__version__']
