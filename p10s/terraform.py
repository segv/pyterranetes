import hcl as pyhcl
from copy import deepcopy


class Configuration():
    def __init__(self, output=None):
        self.output = output
        self.data = {}

    def _merge_in(self, values):
        def rec(a, b):
            for k in b.keys():
                new = b[k]
                if isinstance(new, dict):
                    existing = a.get(k, a)
                    if existing is a:
                        a[k] = new
                    else:
                        if isinstance(existing, dict):
                            rec(existing, new)
                        else:
                            a[k] = new
                else:
                    a[k] = new

        rec(self.data, values)

        return self

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

    def local(self, name, block):
        self._merge_in({'locals': {name: block}})

    def hcl(self, hcl):
        self._merge_in(pyhcl.loads(hcl))

    def __iadd__(self, block):
        self._merge_in(block.data)
        return self

    def __add__(self, block):
        new = Configuration(self.output)
        new.data = deepcopy(self.data)
        return new.__iadd__(block)


class TerraformBlock():
    def render(self):
        return self.data


class Block0(TerraformBlock):
    def __init__(self, block):
        self.data = {
            self.KIND: block or {}
        }


class Block1(TerraformBlock):
    def __init__(self, arg1, block):
        self.data = {
            self.KIND: {
                arg1: block or {}
            }
        }


class Block2(TerraformBlock):
    def __init__(self, arg1, arg2, block):
        self.data = {
            self.KIND: {
                arg1: {
                    arg2: block or {}
                }
            }
        }


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


class Provider(Block1):
    KIND = 'provider'


class Resource(Block2):
    KIND = 'resource'


class Data(Block2):
    KIND = 'data'


class HCL(TerraformBlock):
    def __init__(self, hcl):
        self.data = pyhcl.loads(hcl)
