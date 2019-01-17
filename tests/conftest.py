import pytest
import tempfile
from pathlib import Path


@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent / 'fixtures'


@pytest.fixture(scope="function")
def tmp_dir():
    return Path(tempfile.mkdtemp())


def pytest_addoption(parser):
    parser.addoption("--runslow", action="store_true", default=False, help="run slow tests")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)
