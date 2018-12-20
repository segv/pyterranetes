from p10s.utils import merge_dicts


def test_merge1():
    a = {'a': 1}
    b = {}
    assert {'a': 1} == merge_dicts(a, b)


def test_merge2():
    a = {}
    b = {'a': 1}
    assert {'a': 1} == merge_dicts(a, b)


def test_merge3():
    a = {'a': 1}
    b = {'b': {}}
    assert {'a': 1, 'b': {}} == merge_dicts(a, b)


def test_merge4():
    a = {'b': {'c': True}}
    b = {'b': {'c': {'d': 'e'}}}
    assert {'b': {'c': {'d': 'e'}}} == merge_dicts(a, b)


def test_merge5():
    a = {'a': 1}
    b = {'b': {}}
    c = {'b': {'c': True}}
    c = merge_dicts(a, b, c)
    assert {'a': 1, 'b': {'c': True}} == c

    c = merge_dicts(c, {'b': {'c': {'d': 'e'}}})

    assert {'a': 1, 'b': {'c': {'d': 'e'}}} == c


def test_merge6():
    assert {'a': 1} == merge_dicts({'a': 0},
                                   {'a': 1})
