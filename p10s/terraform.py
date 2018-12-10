import json
from copy import deepcopy
from p10s.loads import hcl
from p10s.utils import merge_dicts
from p10s.context import BaseContext


class TFContext(BaseContext):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.output is None:
            if self.input is not None:
                self.output = self.input.with_suffix('.tf.json')

    def resource(self, type, name, body=None):
        self += Resource(type, name, body)

    def data(self, type, name, body=None):
        self += Data(type, name, body)

    def provider(self, name, body=None):
        self += Provider(name, body)

    def module(self, name, body=None):
        self += Module(name, body)

    def terraform(self, body=None):
        self += Terraform(body)

    def variable(self, name, body=None):
        self += Variable(name, body)

    def output(self, name, body):
        self += Output(name, body)

    def _merge_in(self, values):
        self.data = merge_dicts(self.data, values)
        return self

    def local(self, name, block):
        self._merge_in({'locals': {name: block}})

    def hcl(self, hcl_data):
        self._merge_in((hcl(hcl_data)))

    def __iadd__(self, block):
        if not isinstance(block, (list, tuple)):
            block = [block]
        for b in block:
            self._merge_in(b.data)
        return self

    def __add__(self, block):
        new = TFContext(input=self.input, output=self.output, data=deepcopy(self.data))
        return new.__iadd__(block)

    def render(self):
        with open(self.output, "w") as tf_json:
            tf_json.write(json.dumps(self.data, indent=4, sort_keys=True))


class TerraformBlock():
    def render(self):
        return self.data

    @property
    def body(self):
        return self._body()

    def _body(self):
        raise NotImplementedError()


class NoArgsBlock(TerraformBlock):
    def __init__(self, body):
        self.data = {
            self.KIND: body or {}
        }

    def _body(self):
        return self.data[self.KIND]


class NameBlock(TerraformBlock):
    def __init__(self, name, body):
        self._name = name
        self.data = {
            self.KIND: {
                name: body or {}
            }
        }

    def _body(self):
        return self.data[self.KIND][self.name]

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self.data[self.KIND][name] = self.data[self.KIND][self._name]
        del self.data[self.KIND][self._name]
        self._name = name


class TypeNameBlock(TerraformBlock):
    def __init__(self, type, name, body):
        self._type = type
        self._name = name
        self.data = {
            self.KIND: {
                type: {
                    name: body or {}
                }
            }
        }

    def _body(self):
        return self.data[self.KIND][self._type][self._name]

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, name):
        self.data[self.KIND][name] = self.data[self.KIND][self._type]
        del self.data[self.KIND][self._type]
        self._type = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self.data[self.KIND][self._type][name] = self.data[self.KIND][self._type][self.name]
        del self.data[self.KIND][self._type][self._name]
        self._name = name


class Terraform(NoArgsBlock):
    KIND = 'terraform'


class Variable(NameBlock):
    KIND = 'variable'


class Output(NameBlock):
    KIND = 'output'


class Local(NameBlock):
    KIND = 'local'


class Module(NameBlock):
    KIND = 'module'


class Provider(NameBlock):
    KIND = 'provider'


class Resource(TypeNameBlock):
    KIND = 'resource'


class Data(TypeNameBlock):
    KIND = 'data'


def from_hcl(hcl_string):
    data = hcl(hcl_string)

    blocks = []

    for kind in data.keys():
        if kind == 'terraform':
            blocks.append(Terraform(body=data[kind]))
        if kind in ('variable', 'output', 'local', 'module', 'provider'):
            for name in data[kind].keys():
                if kind == 'variable':
                    cls = Variable
                if kind == 'output':
                    cls = Output
                if kind == 'local':
                    cls = Local
                if kind == 'module':
                    cls = Module
                if kind == 'provider':
                    cls = Provider
                blocks.append(cls(name=name, body=data[kind][name]))
        if kind in ('resource', 'data'):
            for type in data[kind].keys():
                for name in data[kind][type]:
                    if kind == 'resource':
                        cls = Resource
                    if kind == 'data':
                        cls = Data
                    blocks.append(cls(type=type, name=name, body=data[kind][type][name]))

        return blocks
