from p10s.terraform import Terraform


def test_merge1():
    t = Terraform()
    assert t.data == {}


def test_merge2():
    t = Terraform()
    t._merge_in({'a': 1})
    assert {'a': 1} == t.data


def test_merge3():
    t = Terraform()
    t._merge_in({'a': 1})
    t._merge_in({'b': {}})
    assert {'a': 1, 'b': {}} == t.data


def test_merge4():
    t = Terraform()
    t._merge_in({'b': {'c': True}})
    assert {'b': {'c': True}} == t.data
    t._merge_in({'b': {'c': {'d': 'e'}}})
    assert {'b': {'c': {'d': 'e'}}} == t.data


def test_merge5():
    t = Terraform()
    t._merge_in({'a': 1})
    t._merge_in({'b': {}})
    t._merge_in({'b': {'c': True}})
    assert {'a': 1, 'b': {'c': True}} == t.data

    t._merge_in({'b': {'c': {'d': 'e'}}})

    assert {'a': 1, 'b': {'c': {'d': 'e'}}} == t.data
