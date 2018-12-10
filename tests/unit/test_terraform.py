import p10s.terraform as tf


def test_init():
    c = tf.TFContext()
    assert c.data == {}


def test_variable1():
    c = tf.TFContext()
    c.variable('foo')
    assert {'variable': {'foo': {}}} == c.data


def test_variable2():
    c = tf.TFContext()
    c.variable('foo', dict(
        type='string'
    ))
    assert {'variable': {'foo': {'type': 'string'}}} == c.data


def test_add():
    a = tf.TFContext()
    assert {} == a.data
    b = a + tf.Variable('foo', {'type': 'string'})
    assert {} == a.data
    assert {'variable': {'foo': {'type': 'string'}}} == b.data


def test_iadd():
    a = tf.TFContext()
    assert {} == a.data
    a += tf.Variable('foo', {'type': 'string'})
    assert {'variable': {'foo': {'type': 'string'}}} == a.data


def test_multiple_variables():
    c = tf.TFContext()
    c.variable('foo', dict(
        type='string'
    ))
    c.variable('bar', dict(
        default='whatever'
    ))
    assert {'variable': {'foo': {'type': 'string'},
                         'bar': {'default': 'whatever'}}} == c.data


def test_resource():
    c = tf.TFContext()
    c.module('foo1', {
        'source': '../../module/',
        'list_of_things': [1, 2, 3]
    })
    assert {'module': {'foo1': {'source': '../../module/',
                                'list_of_things': [1, 2, 3]}}} == c.data


def test_hcl():
    c1 = tf.TFContext()
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
    c2 = tf.TFContext()
    c2.terraform({'foo': 'bar'})
    c2.resource('type', 'name', {
        'whatever': {
            'here': 'there'
        }
    })
    assert c1.data == c2.data


def test_modify_resource():
    resource = tf.Resource("foo", "bar", {
        "count": 7
    })
    assert resource.body()['count'] == 7
    assert resource.type == 'foo'
    assert resource.name == 'bar'
    resource.body()['count'] = 0
    resource.name = 'name'
    resource.type = 'type'
    assert resource.body()['count'] == 0
    assert resource.name == 'name'
    assert resource.type == 'type'


def test_modify_module():
    module = tf.Module("foo", {
        "count": 7
    })

    module.name = "other"
    module.body()['count'] = 0

    assert {'module': {'other': {'count': 0}}} == module.data
