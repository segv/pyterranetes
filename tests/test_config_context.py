import configparser
import json

import pytest
import yaml

from pathlib import Path

from p10s import cfg
import p10s.config_context


def test_ini(tmp_dir):
    c = cfg.INIContext(tmp_dir / 'test')

    c += {
        'section': {
            'a': 1,
            'b': "2",
        }
    }

    c.render()

    output = Path(tmp_dir / 'test.ini')
    assert output.exists()

    cp = configparser.ConfigParser()
    cp.read(str(output))

    assert cp.sections() == ['section']
    assert sorted(list(cp['section'].keys())) == ["a", "b"]
    assert cp['section']["a"] == "1"
    assert cp['section']["b"] == "2"
    assert cp['section'].getint("a") == 1


DATUM = {
    'section': {
        'a': 1,
        'b': ['c', 2, "2"],
        'd': {
            'e': None,
            'f': True,
        }
    }
}


def test_json(tmp_dir):
    c = cfg.JSONContext(tmp_dir / 'test') + DATUM
    c.render()

    output = Path(tmp_dir / 'test.json')
    assert output.exists()
    out = output.open("r")

    assert json.load(out) == DATUM


def test_yaml(tmp_dir):
    c = cfg.YAMLContext(tmp_dir / 'test') + DATUM
    c.render()

    output = Path(tmp_dir / 'test.yaml')
    assert output.exists()
    out = output.open("r")

    assert yaml.safe_load(out) == DATUM


def test_auto_empty_data():
    a = cfg.AutoData()
    assert a.data() == {}


def test_auto_item1():
    a = cfg.AutoData()
    a['key'] = 'value'
    assert a.data() == {'key': 'value'}


def test_auto_item2():
    a = cfg.AutoData()
    a['top']['bottom'] = 'value'
    assert a.data() == {'top': {'bottom': 'value'}}


def test_auto_item3():
    a = cfg.AutoData()
    a[0] = 'value'
    assert a.data() == ['value']


def test_auto_item4():
    a = cfg.AutoData()
    a[1] = 'value'
    assert a.data() == [None, 'value']


def test_auto_item5():
    a = cfg.AutoData()
    a['a']['b'] = '1'
    a['a']['c']['d'] = '2'
    assert a.data() == {
        'a': {
            'b': '1',
            'c': {
                'd': '2'
            }
        }
    }


def test_auto_item6():
    a = cfg.AutoData()
    a['a'][4]['f'] = 'z'
    assert a.data() == {'a': [None, None, None, None, {'f': 'z'}]}


def test_auto_item7():
    a = cfg.AutoData()
    a['apiVersion'] = 'v1'
    a['spec']['template']['spec']['containers'][0]['image'] = 'foo-bar:latest'
    assert a.data() == {
        'apiVersion': 'v1',
        'spec': {
            'template': {
                'spec': {
                    'containers': [{'image': 'foo-bar:latest'}]
                }
            }
        }
    }


def test_auto_attr1():
    a = cfg.AutoData()
    a.foo = 'bar'
    a.data() == {'foo': 'bar'}


def test_auto_attr2():
    a = cfg.AutoData()
    a.a.b.c[1].d = 'bar'
    a.data() == {'a': {'b': {'c': [None, {'d': 'bar'}]}}}


def test_auto_object_change_type1():
    a = cfg.AutoData()
    a['key'] = '1'
    assert a.data() == {'key': '1'}
    with pytest.raises(p10s.config_context.DataAccessMismatch):
        a[0]


def test_auto_object_change_type2():
    a = cfg.AutoData()
    a[0] = '1'
    assert a.data() == ['1']
    with pytest.raises(p10s.config_context.DataAccessMismatch):
        a['key']


def test_auto_object_invalid_key_type():
    a = cfg.AutoData()
    with pytest.raises(p10s.config_context.InvalidKeyType):
        a['a'][{}]
