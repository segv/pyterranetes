import pytest
from pathlib import Path
from p10s import yaml, json, hcl
from p10s.loads import _data, load_file


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


def test_data_from_path(fixtures_dir):
    path = fixtures_dir / 'sample.yaml'
    expected = path.open().read()
    assert expected == _data(path)


def test_data_from_file(fixtures_dir):
    path = fixtures_dir / 'sample.yaml'
    expected = path.open().read()
    assert expected == _data(path.open())


def test_read_hcl_filename(fixtures_dir):
    assert {'resource': {'a': {'b': {'foo': ['bar']}}}} == hcl(fixtures_dir / 'sample.hcl')


def test_load_file(fixtures_dir):
    assert {'resource': {'a': {'b': {'foo': ['bar']}}}} == load_file(fixtures_dir / 'sample.hcl')
    assert {'foo': True} == load_file(fixtures_dir / 'sample.yaml')


@pytest.mark.parametrize('invalid_filename', [
    'does_not_exist.txt',
    'invalid/file.json',
    'invalid/file.yaml',
    'invalid/file.hcl'
])
def test_load_file_exception(fixtures_dir, invalid_filename):
    with pytest.raises(Exception):
        load_file(fixtures_dir / invalid_filename)
