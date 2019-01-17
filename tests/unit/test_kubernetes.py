import pytest
from p10s import k8s
from collections import OrderedDict
import shutil


@pytest.mark.parametrize('klass,kind', [(k8s.Service, 'Service'),
                                        (k8s.Deployment, 'Deployment')])
def test_render_with_kind(klass, kind):
    rendered = klass({}).render()
    assert rendered['kind'] == kind


def test_single_from_yaml():
    service = k8s.from_yaml("""
apiVersion: v1
kind: Service
    """)
    assert isinstance(service, k8s.Service)
    assert service.data == OrderedDict([('apiVersion', 'v1'),
                                        ('kind', 'Service')])


def test_multiple_from_yaml():
    data = k8s.many_from_yaml("""
---
apiVersion: v1
kind: Service
---
apiVersion: v2
kind: Deployment
    """)
    assert isinstance(data[0], k8s.Service)
    assert isinstance(data[1], k8s.Deployment)
    assert data[0].data == OrderedDict([('apiVersion', 'v1'), ('kind', 'Service')])
    assert data[1].data == OrderedDict([('apiVersion', 'v2'), ('kind', 'Deployment')])


def test_can_not_add_to_context():
    c = k8s.Context()
    with pytest.raises(Exception):
        c += k8s.Service


def test_add_to_body():
    map = k8s.from_yaml("""
kind: ConfigMap
data: {}
    """)

    map.body['data']['foo'] = 'bar'

    assert {'data': OrderedDict([('foo', 'bar')]), 'kind': 'ConfigMap'} == map.render()


def test_recursive_render():
    o = k8s.Data(data=[[k8s.Data(data=4)],
                       {'foo': k8s.Data(data='bar')}])
    assert [[4], {'foo': 'bar'}] == o.render()


def test_update1():
    o = k8s.KubernetesObject(data={'a': 'b'})
    o.update({'a': {'c': 'd'}})
    assert {'a': {'c': 'd'}} == o.render()


def test_update2():
    o = k8s.KubernetesObject(data={'a': 'b'})
    o = o.update({'a': {'c': 'd'}})
    assert {'a': {'c': 'd'}} == o.render()


def test_properties1():
    o = k8s.Deployment()
    o.apiVersion = 'v1'
    o.metadata = {
        'name': 'foobar'
    }
    o.spec = True
    assert {'apiVersion': 'v1',
            'kind': 'Deployment',
            'metadata': {
                'name': 'foobar'},
            'spec': True} == o.render()


def test_properties2():
    o = k8s.Deployment(data={
        'apiVersion': 'v1',
        'kind': 'Deployment',
        'metadata': {
            'name': 'foobar'},
        'spec': True
    })
    assert o.apiVersion == 'v1'
    assert o.metadata == {'name': 'foobar'}
    assert o.spec is True


def test_create_output_dir(fixtures_dir):
    output_dir = fixtures_dir / 'generator_data' / 'simple' / 'does_not_exist'
    output_file = output_dir / 'output.yaml'
    shutil.rmtree(str(output_dir), ignore_errors=True)
    c = k8s.Context(output=output_file)
    c += k8s.Service(dict(foo=42))
    c.render()

    assert output_file.exists()
