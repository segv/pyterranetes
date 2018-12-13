import pytest
from p10s import k8s
from collections import OrderedDict


def test_service1():
    rendered = k8s.Service({}).render()
    assert rendered['kind'] == 'Service'


def test_service2():
    rendered = k8s.Service().render()
    assert rendered['kind'] == 'Service'


def test_single_from_yaml():
    service = k8s.from_yaml("""
apiVersion: v1
kind: Service
    """)
    assert isinstance(service, k8s.Service)
    assert service.data == OrderedDict([('apiVersion', 'v1'), ('kind', 'Service')])


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
    o = k8s.KubernetesObject(data=[
        [k8s.KubernetesObject(data=4)],
        {'foo': k8s.KubernetesObject(data='bar')}])
    assert [[4], {'foo': 'bar'}] == o.render()


def test_update1():
    o = k8s.KubernetesObject(data={'a': 'b'})
    o.update({'a': {'c': 'd'}})
    assert {'a': {'c': 'd'}} == o.render()


def test_update2():
    o = k8s.KubernetesObject(data={'a': 'b'})
    o = o.update({'a': {'c': 'd'}})
    assert {'a': {'c': 'd'}} == o.render()
