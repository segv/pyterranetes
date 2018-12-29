import pytest
from p10s.utils import merge_dicts


@pytest.mark.parametrize("a,b,expected", [
    ({'a': 1}, {}, {'a': 1}),
    ({}, {'a': 1}, {'a': 1}),
    ({'a': 1}, {'b': 1}, {'a': 1, 'b': 1}),
    ({'b': {'c': True}}, {'b': {'c': {'d': 'e'}}}, {'b': {'c': {'d': 'e'}}}),
    ({'a': 0}, {'a': 1}, {'a': 1})
])
def test_merge_2(a, b, expected):
    assert merge_dicts(a, b) == expected


def test_merge_many():
    a = {'a': 1}
    b = {'b': {}}
    c = {'b': {'c': True}}
    c = merge_dicts(a, b, c)
    assert {'a': 1, 'b': {'c': True}} == c

    c = merge_dicts(c, {'b': {'c': {'d': 'e'}}})

    assert {'a': 1, 'b': {'c': {'d': 'e'}}} == c
