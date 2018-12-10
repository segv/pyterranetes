import pytest
from p10s.values import Values


def test_values_invalid_basedir(fixtures_dir):
    with pytest.raises(Exception):
        Values.from_files(fixtures_dir / 'values_data' / 'top' / 'does-not-exist')


def test_values(fixtures_dir):
    v = Values.from_files(fixtures_dir / 'values_data' / 'top' / 'bottom')
    expected = {'shared': 'set at bottom',
                'bottom_only': 'set at bottom',
                'top_only': 'set at top'}
    assert expected == v.values
