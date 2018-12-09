import pytest
from pathlib import Path
from p10s import yaml, json, hcl
from p10s.loads import _data, load_file

FIXTURES = Path(__file__).parent.parent / 'fixtures'


def test_read_yaml_string():
    assert {'foo': True} == yaml("""
foo: true
    """)


def test_read_json_string():
    assert {'foo': True} == json('{"foo": true}')


def test_read_hcl_string():
    assert {'whatever': {'foo': True}} == hcl('whatever { foo = true }')


def test_data_from_string():
    assert "./etc/" == _data("./etc/")


def test_data_from_path():
    path = FIXTURES / 'sample.yaml'
    expected = open(path).read()
    assert expected == _data(path)


def test_data_from_file():
    path = FIXTURES / 'sample.yaml'
    expected = open(path).read()
    assert expected == _data(open(path))


def test_read_hcl_filename():
    assert {'resource': {'a': {'b': {'foo': ['bar']}}}} == hcl(FIXTURES / 'sample.hcl')


def test_load_file():
    assert {'resource': {'a': {'b': {'foo': ['bar']}}}} == load_file(FIXTURES / 'sample.hcl')
    assert {'foo': True} == load_file(FIXTURES / 'sample.yaml')


def test_load_file_exception():
    with pytest.raises(Exception):
        load_file(FIXTURES / 'sample.txt')
