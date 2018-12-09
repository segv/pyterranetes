import pytest
from pathlib import Path
from p10s.values import Values


FIXTURES = Path(__file__).parent.parent / 'fixtures'


def test_values_invalid_basedir():
    with pytest.raises(Exception):
        Values.from_files(FIXTURES / 'values_data' / 'top' / 'does-not-exist')


def test_values():
    v = Values.from_files(FIXTURES / 'values_data' / 'top' / 'bottom')
    expected = {'shared': 'set at bottom',
                'bottom_only': 'set at bottom',
                'top_only': 'set at top'}
    assert expected == v.values
