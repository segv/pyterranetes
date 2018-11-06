from p10s.terraform import Terraform


def test_init():
    t = Terraform()
    assert t.data == {}


def test_variable1():
    t = Terraform()
    t.variable('foo')
    assert {'variable': {'foo': {}}} == t.data


def test_variable2():
    t = Terraform()
    t.variable('foo', type='string')
    assert {'variable': {'foo': {'type': 'string'}}} == t.data


def test_multiple_variables():
    t = Terraform()
    t.variable('foo', type='string')
    t.variable('bar', default='whatever')
    assert {'variable': {'foo': {'type': 'string'},
                         'bar': {'default': 'whatever'}}} == t.data


def test_resource():
    t = Terraform()
    t.module('foo1', {
        'source': '../../module/',
        'list_of_things': [1, 2, 3]
    })
    assert {'module': {'foo1': {'source': '../../module/',
                                'list_of_things': [1, 2, 3]}}} == t.data


def test_hcl():
    t1 = Terraform()
    t1.hcl("""
    terraform {
      foo = "bar"
    }

    resource "type" "name" {
      whatever {
        here = "there"
      }
    }

    """)
    t2 = Terraform()
    t2.terraform({'foo': 'bar'})
    t2.resource('type', 'name', {
        'whatever': {
            'here': 'there'
        }
    })
    assert t1.data == t2.data
