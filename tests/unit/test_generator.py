import json
from pathlib import Path
from p10s.generator import Generator
import sys
from copy import deepcopy


def test_find_p10s_files(fixtures_dir):
    base = fixtures_dir / 'generator_data' / 'find_p10s_files'
    top = base / 'top.p10s'
    bottom = base / 'sub1' / 'sub2' / 'bottom.p10s'

    expected = [top, bottom]
    actual = list(Generator().p10s_files(base))
    assert expected == actual


def test_add_dir_to_sys_path(monkeypatch, fixtures_dir):
    base = fixtures_dir / 'generator_data' / 'find_p10s_files'
    target = base / 'pyterranetes'
    start = base / 'sub1' / 'sub2'
    with monkeypatch.context() as m:
        old_path = deepcopy(sys.path)
        m.setattr('sys.path', sys.path)
        Generator().add_pyterranetes_dir(start)
        assert target == Path(sys.path[0])
        assert old_path == sys.path[1:]


def test_compute_output_file(fixtures_dir):
    input = fixtures_dir / 'generator_data' / 'simple' / 'simple.p10s'
    g = Generator()
    outputs = g.compile(input)
    assert len(outputs) == 1
    output = outputs[0]
    assert output.input == input
    assert output.output == input.with_suffix('.tf.json')
    assert {'resource':
            {'a':
             {'b': {'count': 1},
              'c': {'count': 2}},
             'b':
             {'b': {'count': 3}}}} == output.data


def test_generate(fixtures_dir):
    input = fixtures_dir / 'generator_data' / 'simple' / 'simple.p10s'
    g = Generator()
    g.generate(input)
    output = fixtures_dir / 'generator_data' / 'simple' / 'simple.tf.json'
    assert output.exists()
    output_data = json.load(open(output))
    assert {'resource':
            {'a':
             {'b': {'count': 1},
              'c': {'count': 2}},
             'b':
             {'b': {'count': 3}}}} == output_data


def test_generate_with_lib1(fixtures_dir):
    input = fixtures_dir / 'generator_data' / 'with_lib' / 'top.p10s'
    g = Generator()
    g.generate(input)
    output = fixtures_dir / 'generator_data' / 'with_lib' / 'top.tf.json'
    assert output.exists()
    output_data = json.load(open(output))
    assert {'provider': {'whatever': {}}} == output_data


def test_generate_with_lib2(fixtures_dir):
    input = fixtures_dir / 'generator_data' / 'with_lib' / 'sub' / 'bottom.p10s'
    g = Generator()
    g.generate(input)
    output = fixtures_dir / 'generator_data' / 'with_lib' / 'sub' / 'bottom.tf.json'
    assert output.exists()
    output_data = json.load(open(output))
    assert {'provider': {'whatever': {}}} == output_data
