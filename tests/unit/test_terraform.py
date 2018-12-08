import p10s.terraform as tf


def test_init():
    c = tf.Configuration()
    assert c.data == {}


def test_variable1():
    c = tf.Configuration()
    c.variable('foo')
    assert {'variable': {'foo': {}}} == c.data


def test_variable2():
    c = tf.Configuration()
    c.variable('foo', dict(
        type='string'
    ))
    assert {'variable': {'foo': {'type': 'string'}}} == c.data


def test_add():
    a = tf.Configuration()
    assert {} == a.data
    b = a + tf.Variable('foo', {'type': 'string'})
    assert {} == a.data
    assert {'variable': {'foo': {'type': 'string'}}} == b.data


def test_iadd():
    a = tf.Configuration()
    assert {} == a.data
    a += tf.Variable('foo', {'type': 'string'})
    assert {'variable': {'foo': {'type': 'string'}}} == a.data


def test_multiple_variables():
    c = tf.Configuration()
    c.variable('foo', dict(
        type='string'
    ))
    c.variable('bar', dict(
        default='whatever'
    ))
    assert {'variable': {'foo': {'type': 'string'},
                         'bar': {'default': 'whatever'}}} == c.data


def test_resource():
    c = tf.Configuration()
    c.module('foo1', {
        'source': '../../module/',
        'list_of_things': [1, 2, 3]
    })
    assert {'module': {'foo1': {'source': '../../module/',
                                'list_of_things': [1, 2, 3]}}} == c.data


def test_hcl():
    c1 = tf.Configuration()
    c1.hcl("""
    terraform {
      foo = "bar"
    }

    resource "type" "name" {
      whatever {
        here = "there"
      }
    }

    """)
    c2 = tf.Configuration()
    c2.terraform({'foo': 'bar'})
    c2.resource('type', 'name', {
        'whatever': {
            'here': 'there'
        }
    })
    assert c1.data == c2.data
