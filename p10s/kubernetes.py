from copy import deepcopy

from p10s.context import BaseContext
from p10s.loads import yaml, yaml_all, ruamel


class K8SContext(BaseContext):
    output_file_extension = '.yaml'

    def __init__(self, *args, data=None, **kwargs):
        if data is None:
            self.data = []
        else:
            self.data = data

        super().__init__(*args, **kwargs)

    def __iadd__(self, object):
        if not isinstance(object, (list, tuple)):
            objects = [object]
        else:
            objects = object
        for o in objects:
            if isinstance(o, KubernetesObject):
                self.data.append(o)
            else:
                raise Exception("Can't add %s to %s, is not of type KubernetesObject", o, self)
        return self

    def __add__(self, block):
        new = K8SContext(input=self.input,
                         output=self.output,
                         data=deepcopy(self.data))
        return new.__iadd__(block)

    def render(self):
        with open(self.output, "w") as out:
            ruamel.dump_all([data.render() for data in self.data],
                            out)


class KubernetesObject():
    def __init__(self, data=None):
        if data is None:
            self.data = {}
        else:
            self.data = data

    def render(self):
        if 'kind' not in self.data:
            self.data['kind'] = self.KIND
        return self.data

    @property
    def body(self):
        return self.data


class Deployment(KubernetesObject):
    KIND = 'Deployment'


class ConfigMap(KubernetesObject):
    KIND = 'ConfigMap'


class Service(KubernetesObject):
    KIND = 'Service'


def _data_to_object(data):
    kind = data.get('kind', None)
    if kind is not None:
        cls = None
        if kind == 'Deployment':
            cls = Deployment
        if kind == 'ConfigMap':
            cls = ConfigMap
        if kind == 'Service':
            cls = Service
        return cls(data=data)
    else:
        raise Exception("Missing kind property on %s", data)


def from_yaml(yaml_string):
    return _data_to_object(yaml(yaml_string))


def many_from_yaml(yaml_string):
    return [_data_to_object(data) for data in yaml_all(yaml_string)]
