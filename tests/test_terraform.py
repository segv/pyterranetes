import pytest
import p10s.terraform as tf
import shutil
from copy import deepcopy


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


def test_module():
    c = tf.Context()
    c += tf.Module('foo1', {
        'source': '../../module/',
        'list_of_things': [1, 2, 3]
    })
    assert {'module': {'foo1': {'source': '../../module/',
                                'list_of_things': [1, 2, 3]}}} == c.data


def test_resource():
    c = tf.Context()
    c += tf.Resource("type", "name", dict(
        var='value'
    ))
    assert {'resource': {'type': {'name': {'var': 'value'}}}} == c.data


def test_update1():
    r = tf.Resource(type="t", name="n", body=dict(
    ))
    r.update(dict(
        type="other",
        name="nother"
    ))

    assert {'resource': {'t': {'n': {'type': 'other', 'name': 'nother'}}}} == r.data


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


def test_many_from_hcl_unknown_key():
    with pytest.raises(tf.HCLUnknownBlockError):
        tf.many_from_hcl("""key { }""")


def test_many_from_hcl_no_data():
    with pytest.raises(tf.HCLParseError):
        tf.many_from_hcl(""" """)


def test_from_hcl_no_data():
    with pytest.raises(tf.HCLParseError):
        tf.from_hcl(""" """)


def test_from_hcl_no_data2():
    try:
        tf.from_hcl(""" """)
    except tf.HCLParseError as e:
        assert str(e).startswith("Unable to parse")
    else:
        pytest.fail("from_hcl did not raise an exception")


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


def test_many_from_hcl_order():
    c = tf.Context()
    many = tf.many_from_hcl("""
    variable "" {
      default = "1"
    }

    variable "a" {
      default = "1"
    }

    variable "a/b" {
      default = "1"
    }

    variable "a/b/c" {
      default = "1"
    }

    """)
    assert [tf.Variable(name="", body={'default': '1'}),
            tf.Variable(name="a", body={'default': '1'}),
            tf.Variable(name="a/b", body={'default': '1'}),
            tf.Variable(name="a/b/c", body={'default': '1'})] == many


@pytest.mark.parametrize("hcl,data", [("""terraform {
                                            foo = "bar"
                                          }
                                          resource "type" "name" {
                                             whatever {
                                               here = "there"
                                             }
                                           }
                                          """,
                                       {'terraform': {'foo': 'bar'},
                                        'resource': {
                                            'type': {
                                                'name': {
                                                    'whatever': {
                                                        'here': 'there'
                                                    }
                                                }
                                            }
                                        }}),
                                      ("""locals {
                                            other {
                                              nested {
                                                value = "value"
                                              }
                                            }
                                          }

                                          locals {
                                            locals = "whatever"
                                          }
                                      """,
                                       {'locals': {
                                           'other': {
                                               'nested': {
                                                   'value': 'value'
                                               }
                                           },
                                           'locals': 'whatever'
                                       }
                                       }),
                                      ("""resource "foo" "bar" {
                                            data1 = <<HEREDOC
                                             this is a test
                                          HEREDOC
                                            data2 = "this is not a test"
                                          }
                                      """,
                                       {'resource':
                                        {'foo': {
                                            'bar': {
                                                'data1': '                                             this is a test\n'
                                                         '                                          ',
                                                'data2': 'this is not a test'}}}})],
                         ids=['two blocks', 'two locals blocs', 'heredoc'])
def test_hcl_as_data(hcl, data):
    c1 = tf.Context()
    c1 += tf.many_from_hcl(hcl)
    assert data == c1.data


def test_hcl_nested_named_block():
    c = tf.Context()
    c += tf.many_from_hcl("""
terraform {
  backend "foo" {
    foo = "bar"
    bar = ["baz"]

    map = {
      a = "b"
    }
  }
}
""")
    assert {
        'terraform': {
            'backend': {
                'foo': {
                    'foo': 'bar',
                    'bar': ['baz'],
                    'map': {
                        'a': 'b'
                    }
                }
            }
        }
    } == c.data


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


def test_share_resource():
    t = tf.Variable("var1", dict(default=1))
    c = tf.Context()

    c += t
    t.name = 'var2'
    c += t

    assert c.data == {'variable': {'var2': {'default': 1}}}


def test_copy_resource():
    t = tf.Variable("var1", dict(default=1))
    c = tf.Context()

    c += deepcopy(t)
    t.name = 'var2'
    c += t

    assert c.data == {'variable': {'var1': {'default': 1},
                                   'var2': {'default': 1}}}


def test_duplicate_variable():
    v1 = tf.Variable("var1", dict(default=1))
    v2 = tf.Variable("var1", dict(other=42))

    c = tf.Context(strict=True)
    c += v1
    with pytest.raises(tf.DuplicateBlockError):
        c += v2


def test_duplicate_resource():
    r1 = tf.Resource("type", "name", dict(var1='val1'))
    r2 = tf.Resource("type", "name", dict(var2='val2'))

    c = tf.Context(strict=True)
    c += r1
    with pytest.raises(tf.DuplicateBlockError):
        c += r2


def test_duplicate_terraform():
    t1 = tf.Terraform(dict(var1='val1'))
    t2 = tf.Terraform(dict(var2='val2'))

    c = tf.Context(strict=True)
    c += t1
    with pytest.raises(tf.DuplicateBlockError):
        c += t2


def test_output1():
    o = tf.Output(name='foo')
    assert o.data == {'output': {'foo': {}}}


def test_output2():
    o = tf.Output(name='foo', body='bar')
    assert o.data == {'output': {'foo': 'bar'}}


def test_output3():
    o = tf.Output(aws_whatever="${var.other_thing}")
    assert o.data == {'output': {'aws_whatever': {'value': "${var.other_thing}"}}}


def test_output4():
    with pytest.raises(Exception):
        tf.Output(a='b', c='d')


def test_module_name():
    m = tf.from_hcl("""module "X" { var = "value" }""")
    m.name = "X"
    assert {'module': {'X': {'var': 'value'}}} == m.data


def test_create_output_dir(fixtures_dir):
    output_dir = fixtures_dir / 'generator_data' / 'simple' / 'does_not_exist'
    output_file = output_dir / 'output.tf.json'
    shutil.rmtree(str(output_dir), ignore_errors=True)
    c = tf.Context(output=output_file)
    c += tf.Terraform(dict(foo=42))
    c.render()

    assert output_file.exists()


def test_variables():
    c = tf.Context()
    c += tf.variables(
        foo=42,
        bar='whatever'
    )
    assert {'variable': {'foo': {'default': 42},
                         'bar': {'default': 'whatever'}}} == c.data


def test_outputs():
    c = tf.Context()
    c += tf.outputs(
        a='b',
        c='${var.c}')
    assert {'output': {'a': {'value': 'b'},
                       'c': {'value': '${var.c}'}}} == c.data


def test_false_body():
    t = tf.Resource("type", "name", 0)
    assert t.data == {'resource': {'type': {'name': 0}}}

    t = tf.Module("name", "")
    assert t.data == {'module': {'name': ""}}


def test_implicit_resource():
    a = tf.Context()

    a.resource.a.b = {'k': 'v1'}
    a.resource.a.c = {'k': 'v2'}

    b = tf.Context()
    b += tf.Resource("a", "b", {'k': 'v1'})
    b += tf.Resource("a", "c", {'k': 'v2'})

    assert a.data == b.data


def test_implicit_module():
    c = tf.Context()

    c.module.name = {}

    assert {'module': {'name': {}}} == c.data


def test_implicit_variable():
    c = tf.Context()

    c.variable.name = 'foo'

    assert {'variable': {'name': {'default': 'foo'}}} == c.data
