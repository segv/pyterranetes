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
    c = k8s.K8SContext()
    with pytest.raises(Exception):
        c += k8s.Service


def test_add_to_body():
    map = k8s.from_yaml("""
kind: ConfigMap
data: {}
    """)

    map.body['data']['foo'] = 'bar'

    assert {'data': OrderedDict([('foo', 'bar')]), 'kind': 'ConfigMap'} == map.render()
