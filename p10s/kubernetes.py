from copy import deepcopy

from p10s.context import BaseContext
from p10s.loads import yaml, yaml_all, ruamel
from p10s.utils import merge_dicts


class Context(BaseContext):
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
        new = Context(input=self.input,
                      output=self.output,
                      data=deepcopy(self.data))
        return new.__iadd__(block)

    def render(self):
        with open(self.output, "w") as out:
            ruamel.dump_all([data.render() for data in self.data],
                            out)


class KubernetesObject():
    KIND = None

    def __init__(self, data=None):
        if data is None:
            self.data = {}
        else:
            self.data = data

    def render(self):
        if (self.KIND is not None) and ('kind' not in self.data):
            self.data['kind'] = self.KIND

        def _rec(object):
            if isinstance(object, (list, tuple)):
                return [_rec(o) for o in object]
            elif isinstance(object, dict):
                return {_rec(k): _rec(v) for k, v in object.items()}
            elif isinstance(object, KubernetesObject):
                return object.render()
            else:
                return object

        return _rec(self.data)

    @property
    def body(self):
        return self.data

    def update(self, data):
        self.data = merge_dicts(self.data, data)
        return self

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
