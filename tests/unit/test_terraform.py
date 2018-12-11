import pytest
import p10s.terraform as tf


def test_init():
    c = tf.Context()
    assert c.data == {}


def test_variable1():
    c = tf.Context()
    c += tf.Variable('foo')
    assert {'variable': {'foo': {}}} == c.data


def test_variable2():
    c = tf.Context()
    c += tf.Variable('foo', dict(
        type='string'
    ))
    assert {'variable': {'foo': {'type': 'string'}}} == c.data


def test_add():
    a = tf.Context()
    assert {} == a.data
    b = a + tf.Variable('foo', {'type': 'string'})
    assert {} == a.data
    assert {'variable': {'foo': {'type': 'string'}}} == b.data


def test_iadd():
    a = tf.Context()
    assert {} == a.data
    a += tf.Variable('foo', {'type': 'string'})
    assert {'variable': {'foo': {'type': 'string'}}} == a.data


def test_multiple_variables():
    c = tf.Context()
    c += tf.Variable('foo', dict(
        type='string'
    ))
    c += tf.Variable('bar', dict(
        default='whatever'
    ))
    assert {'variable': {'foo': {'type': 'string'},
                         'bar': {'default': 'whatever'}}} == c.data


def test_resource():
    c = tf.Context()
    c += tf.Module('foo1', {
        'source': '../../module/',
        'list_of_things': [1, 2, 3]
    })
    assert {'module': {'foo1': {'source': '../../module/',
                                'list_of_things': [1, 2, 3]}}} == c.data


def test_hcl_as_object():
    c1 = tf.Context()
    c1 += tf.many_from_hcl("""
    terraform {
      foo = "bar"
    }

    resource "type" "name" {
      whatever {
        here = "there"
      }
    }

    """)
    c2 = tf.Context()
    c2 += tf.Terraform({'foo': 'bar'})
    c2 += tf.Resource('type', 'name', {
        'whatever': {
            'here': 'there'
        }
    })
    assert c1.data == c2.data


def test_single_hcl_raises():
    with pytest.raises(Exception):
        tf.from_hcl("""
            terraform {
              foo = "bar"
            }

            resource "type" "name" {
              whatever {
                here = "there"
              }
            }
        """)


def test_single_parse():
    c1 = tf.Context()
    c1 += tf.many_from_hcl("""
        terraform {
          foo = "bar"
        }
    """)
    c2 = tf.Context()
    c2 += tf.Terraform({'foo': 'bar'})
    assert c1.data == c2.data


def test_hcl_as_data():
    c1 = tf.Context()
    c1 += tf.many_from_hcl("""
    terraform {
      foo = "bar"
    }

    resource "type" "name" {
      whatever {
        here = "there"
      }
    }

    """)
    assert {'terraform': {'foo': 'bar'},
            'resource': {
                'type': {
                    'name': {
                        'whatever': {
                            'here': 'there'
                        }
                    }
                }
            }} == c1.data


def test_modify_resource():
    resource = tf.Resource("foo", "bar", {
        "count": 7
    })
    assert resource.body['count'] == 7
    assert resource.type == 'foo'
    assert resource.name == 'bar'
    resource.body['count'] = 0
    resource.name = 'name'
    resource.type = 'type'
    assert resource.body['count'] == 0
    assert resource.name == 'name'
    assert resource.type == 'type'


def test_modify_module():
    module = tf.Module("foo", {
        "count": 7
    })

    module.name = "other"
    module.body['count'] = 0

    assert {'module': {'other': {'count': 0}}} == module.data
