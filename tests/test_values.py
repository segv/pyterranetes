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
    with values({'bar': 'top'}, foo='top'):
        with values(foo='bottom'):
            assert _inner() == 'bottom'


def test_value_inheritence2():
    with values(foo='top', bar='top'):
        _set_foo()
        assert _inner() == 'inner'
        with values(foo='bottom'):
            assert _inner() == 'bottom'


def test_value_inheritence3():
    with values(foo='top', bar='top'):
        with values(foo='bottom'):
            assert value('bar') == 'top'
            assert value('foo') == 'bottom'


def test_value_values_args1():
    with values({'a': 'top_first'}, {'a': 'top_second'}, a='top_third'):
        assert value('a') == 'top_third'


def test_value_values_args2():
    with values({'a': 'top_A'}, {'b': 'top_B'}):
        with values(b='bottom_B'):
            assert value('b') == 'bottom_B'


def test_value_values_args3():
    with values({'a': 'top_A'}):
        with values(a='mid_A'):
            with values({}, {'a': 'bottom_A'}):
                assert value('a') == 'bottom_A'


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


def test_values_add1(mocker):
    a = Values({'val': 'A'})
    b = Values({'val': 'B'})

    a += b

    assert {'val': 'B'} == a.values
    assert {'val': 'B'} == b.values


def test_values_add2(mocker):
    a = Values({'val': 'A'})
    b = Values({'val': 'B'})

    c = a + b

    assert {'val': 'A'} == a.values
    assert {'val': 'B'} == b.values
    assert {'val': 'B'} == c.values
