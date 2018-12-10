import p10s.terraform as tf


def test_merge1():
    c = tf.TFContext()
    assert c.data == {}


def test_merge2():
    c = tf.TFContext()
    c._merge_in({'a': 1})
    assert {'a': 1} == c.data


def test_merge3():
    c = tf.TFContext()
    c._merge_in({'a': 1})
    c._merge_in({'b': {}})
    assert {'a': 1, 'b': {}} == c.data


def test_merge4():
    c = tf.TFContext()
    c._merge_in({'b': {'c': True}})
    assert {'b': {'c': True}} == c.data
    c._merge_in({'b': {'c': {'d': 'e'}}})
    assert {'b': {'c': {'d': 'e'}}} == c.data


def test_merge5():
    c = tf.TFContext()
    c._merge_in({'a': 1})
    c._merge_in({'b': {}})
    c._merge_in({'b': {'c': True}})
    assert {'a': 1, 'b': {'c': True}} == c.data

    c._merge_in({'b': {'c': {'d': 'e'}}})

    assert {'a': 1, 'b': {'c': {'d': 'e'}}} == c.data
