import pytest
import json
import os
from p10s.generator import Generator, P10SScript, _global_state
import sys
from copy import deepcopy


def test_find_p10s_files(fixtures_dir):
    base = fixtures_dir / 'generator_data' / 'find_p10s_files'
    top = base / 'top.p10s'
    bottom = base / 'sub1' / 'sub2' / 'bottom.p10s'

    expected = [top, bottom]
    actual = list(Generator()._p10s_scripts(base))
    assert expected == actual


def test_find_p10s_script_does_not_exist(fixtures_dir):
    with pytest.raises(FileNotFoundError):
        list(Generator()._p10s_scripts(fixtures_dir / 'does_not_exist.p10s'))


def test_find_pyterranetes_dir_as_sibling(fixtures_dir):
    script = P10SScript(fixtures_dir / 'generator_data' / 'with_lib' / 'top.p10s')
    assert script.pyterranetes_dir == fixtures_dir / 'generator_data' / 'with_lib' / 'pyterranetes'


def test_find_pyterranetes_dir_as_parent(fixtures_dir):
    script = P10SScript(fixtures_dir / 'generator_data' / 'with_lib' / 'sub' / 'bottom.p10s')
    assert script.pyterranetes_dir == fixtures_dir / 'generator_data' / 'with_lib' / 'pyterranetes'


def test_find_pyterranetes_dir_as_grandparent(fixtures_dir):
    script = P10SScript(fixtures_dir / 'generator_data' / 'with_lib' / 'sub' / 'sub' / 'underground.p10s')
    assert script.pyterranetes_dir == fixtures_dir / 'generator_data' / 'with_lib' / 'pyterranetes'


def test_global_state_set_sys_path(monkeypatch, fixtures_dir):
    base = fixtures_dir / 'generator_data' / 'with_lib'
    target = base / 'pyterranetes'
    start = base / 'sub'
    here = os.getcwd()
    with monkeypatch.context() as m:
        old_path = deepcopy(sys.path)
        m.setattr('sys.path', sys.path)
        try:
            os.chdir(str(start))
            with _global_state(dir=fixtures_dir, extra_sys_paths=[target]):
                assert [str(target)] + old_path == sys.path
                assert os.getcwd() == str(fixtures_dir)
            assert old_path == sys.path
            assert os.getcwd() == str(start)
        finally:
            os.chdir(here)


def test_global_state_import_works(monkeypatch, fixtures_dir):
    base = fixtures_dir / 'generator_data' / 'with_lib'
    target = base / 'pyterranetes'
    start = base / 'sub'
    here = os.getcwd()

    try:
        os.chdir(str(start))
        with _global_state(dir=fixtures_dir, extra_sys_paths=[target]):
            try:
                from import_test import SUCCESS  # noqa: F401
            except ModuleNotFoundError:
                pytest.fail("unable to import infra")
    finally:
        os.chdir(here)


def test_compute_p10s_script(fixtures_dir):
    input = fixtures_dir / 'generator_data' / 'simple' / 'simple.p10s'
    script = P10SScript(filename=input)
    # g = Generator()
    # outputs = g.compile(input)
    script.compile()
    contexts = script.contexts
    assert len(contexts) == 1
    context = contexts[0]
    assert context.input == input
    assert context.output == input.with_suffix('.tf.json')
    assert {'resource':
            {'a':
             {'b': {'count': 1},
              'c': {'count': 2}},
             'b':
             {'b': {'count': 3}}}} == context.data


def test_generate(fixtures_dir):
    input = fixtures_dir / 'generator_data' / 'simple' / 'simple.p10s'
    g = Generator()
    g.generate(input)
    output = fixtures_dir / 'generator_data' / 'simple' / 'simple.tf.json'
    assert output.exists()
    output_data = json.load(output.open())
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
    output_data = json.load(output.open())
    assert {'provider': {'whatever': {}}} == output_data


def test_generate_with_lib2(fixtures_dir):
    input = fixtures_dir / 'generator_data' / 'with_lib' / 'sub' / 'bottom.p10s'
    g = Generator()
    g.generate(input)
    output = fixtures_dir / 'generator_data' / 'with_lib' / 'sub' / 'bottom.tf.json'
    assert output.exists()
    output_data = json.load(output.open())
    assert {'provider': {'whatever': {}}} == output_data


def test_generate_k8s(fixtures_dir):
    input = fixtures_dir / 'generator_data' / 'simple' / 'single_k8s.p10s'
    g = Generator()
    g.generate(input)
    output = fixtures_dir / 'generator_data' / 'simple' / 'single_k8s.yaml'
    assert output.exists()
    output_data = output.open().read()
    assert """apiVersion: v1
data: {}
kind: ConfigMap
metadata:
  labels:
    env: prd
    grafana_dashboard: '1'
  name: foobar
""" == output_data


def test_pwd(fixtures_dir):
    input = fixtures_dir / 'generator_data' / 'simple' / 'pwd.p10s'
    g = Generator()
    g.generate(input)
    output = fixtures_dir / 'generator_data' / 'simple' / 'pwd.tf.json'
    assert output.exists()
    output_data = json.load(output.open())
    assert {'data':
            {'bar':
             {'foo': {'pwd': str(input.parent.resolve())}}}} == output_data


def test_register_context(fixtures_dir):
    input = fixtures_dir / 'generator_data' / 'register_context' / 'test.p10s'
    g = Generator()
    g.generate(input)

    s = fixtures_dir / 'generator_data' / 'register_context' / 'test.tf.json'
    s2 = fixtures_dir / 'generator_data' / 'register_context' / 'static_2.tf.json'
    da = fixtures_dir / 'generator_data' / 'register_context' / 'dynamic_a.tf.json'
    db = fixtures_dir / 'generator_data' / 'register_context' / 'dynamic_b.tf.json'
    dc = fixtures_dir / 'generator_data' / 'register_context' / 'dynamic_c.tf.json'

    assert s.exists()
    assert {'module': {'static': {'var': 's'}}} == json.load(s.open())

    assert s2.exists()
    assert {'module': {'static_2': {'var': 's2'}}} == json.load(s2.open())

    assert da.exists()
    assert {'module': {'dynamic_a': {}}} == json.load(da.open())

    assert db.exists()
    assert {'module': {'dynamic_b': {}}} == json.load(db.open())

    assert dc.exists()
    assert {'module': {'dynamic_c': {}}} == json.load(dc.open())
