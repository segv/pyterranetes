import pytest
from p10s.values import Values, values, value, set_value


def test_values_invalid_basedir(fixtures_dir):
    with pytest.raises(Exception):
        Values.from_files(fixtures_dir / 'values_data' / 'top' / 'does-not-exist')


def test_values(fixtures_dir):
    v = Values.from_files(fixtures_dir / 'values_data' / 'top' / 'bottom')
    expected = {'shared': 'set at bottom',
                'bottom_only': 'set at bottom',
                'top_only': 'set at top'}
    assert expected == v.values


def _inner():
    return value('foo')


def _set_foo():
    set_value('foo', 'inner')


def test_value_inheritence1():
    with values(foo='top'):
        with values(foo='bottom'):
            assert _inner() == 'bottom'


def test_value_inheritence2():
    with values(foo='top'):
        _set_foo()
        assert _inner() == 'inner'
        with values(foo='bottom'):
            assert _inner() == 'bottom'


def test_values_as_dict1():
    v = Values()
    v['a'] = 'b'
    assert {'a': 'b'} == v.values


def test_values_as_dict2():
    v = Values()
    v['a'] = 'b'
    del v['a']
    assert v.values == {}


def test_values_as_dict3():
    v = Values()
    v['a'] = 'b'
    assert v.get('b', False) is False


def test_values_as_dict4():
    v = Values()
    v['a'] = 'b'
    assert len(v) == len(v.values)


def test_values_from_environ(mocker):
    mocker.patch('os.environ', new={'var': 'value'})
    values = Values.from_environ()
    assert {'var': 'value'} == values.values
