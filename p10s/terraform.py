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
                self.output = self.input.with_suffix('.tfjson')

    def resource(self, type, name, block=None):
        self += Resource(type, name, block)

    def data(self, type, name, block=None):
        self += Data(type, name, block)

    def provider(self, name, block=None):
        self += Provider(name, block)

    def module(self, name, block=None):
        self += Module(name, block)

    def terraform(self, block=None):
        self += Terraform(block)

    def variable(self, name, block=None):
        self += Variable(name, block)

    def output(self, name, block):
        self += Output(name, block)

    def _merge_in(self, values):
        self.data = merge_dicts(self.data, values)
        return self

    def local(self, name, block):
        self._merge_in({'locals': {name: block}})

    def hcl(self, hcl_data):
        self._merge_in((hcl(hcl_data)))

    def __iadd__(self, block):
        self._merge_in(block.data)
        return self

    def __add__(self, block):
        new = TFContext(input=self.input, output=self.output, data=deepcopy(self.data))
        return new.__iadd__(block)

    def render(self):
        with open(self.output, "w") as tfjson:
            tfjson.write(json.dumps(self.data, indent=4, sort_keys=True))


class TerraformBlock():
    def render(self):
        return self.data

    def body(self):
        raise NotImplementedError()


class Block0(TerraformBlock):
    def __init__(self, block):
        self.data = {
            self.KIND: block or {}
        }

    def body(self):
        return self.data[self.KIND]


class Block1(TerraformBlock):
    def __init__(self, arg1, block):
        self.arg1 = arg1
        self.data = {
            self.KIND: {
                arg1: block or {}
            }
        }

    def body(self):
        return self.data[self.KIND][self.arg1]


class Block2(TerraformBlock):
    def __init__(self, arg1, arg2, block):
        self.arg1 = arg1
        self.arg2 = arg2
        self.data = {
            self.KIND: {
                arg1: {
                    arg2: block or {}
                }
            }
        }

    def body(self):
        return self.data[self.KIND][self.arg1][self.arg2]


class Terraform(Block0):
    KIND = 'terraform'


class Variable(Block1):
    KIND = 'variable'


class Output(Block1):
    KIND = 'output'


class Local(Block1):
    KIND = 'local'


class Module(Block1):
    KIND = 'module'

    @property
    def name(self):
        return self.arg1

    @name.setter
    def name(self, name):
        self.data[self.KIND][name] = self.data[self.KIND][self.arg1]
        del self.data[self.KIND][self.arg1]
        self.arg1 = name


class Provider(Block1):
    KIND = 'provider'


class Resource(Block2):
    KIND = 'resource'

    @property
    def type(self):
        return self.arg1

    @type.setter
    def type(self, name):
        self.data[self.KIND][name] = self.data[self.KIND][self.arg1]
        del self.data[self.KIND][self.arg1]
        self.arg1 = name

    @property
    def name(self):
        return self.arg2

    @name.setter
    def name(self, name):
        self.data[self.KIND][self.arg1][name] = self.data[self.KIND][self.arg1][self.arg2]
        del self.data[self.KIND][self.arg1][self.arg2]
        self.arg2 = name


class Data(Block2):
    KIND = 'data'


class HCL(TerraformBlock):
    def __init__(self, hcl_string):
        self.data = hcl(hcl_string)
