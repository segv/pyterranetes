"""
Generating terraform with pyterranetes is, as with kubernetes, just a
question of writing a p10s script which creates a
``terraform.Context`` object and adds terraform blocks to it:

.. code-block:: python

    from p10s import tf

    c = tf.Context()

    c += tf.Variable("foo", dict(
        default=0
    ))

    c += tf.Resource("type", "name", dict(
        var = 'value'
    ))

    ...


For each terraform configuration block there is a corresponding python
class. Depending on the block type and how it's used some of the
classes provid convenience methods and constructors. All of the
classes have a ``.body`` property representing the data inside the
block. This body is stored as a python dict with a simple mapping from
python to hcl:

``key: value``
    a line setting ``key`` to ``value`` (a string or a number)
``key: [ ... ]``
    a line setting ``key`` to a list
``key: { ... }``
    a nested block ``key { ... }``

for example the following ``tf.Module`` object:

.. code-block:: python

    tf.Module(name="name", body={
        'a': {
            'b': 2,
            'c': {
                'd': ["start", "end"]
            }
        }
    })

would generate the following hcl:

.. code-block:: terraform

    module "name" {
      a = {
        b = 2
        c = {
          d = ["start", "end"]
        }
      }
    }

There are 3 different categories of terraform blocks:

Blocks that don't have any properties other than ``.body``:
    :py:class:`terraform <p10s.terraform.Terraform>`, and
    :py:class:`locals <p10s.terraform.Locals>`.
Blocks that also have a name property:
    :py:class:`provider <p10s.terraform.Provider>`,
    :py:class:`variable <p10s.terraform.Variable>`, and
    :py:class:`output <p10s.terraform.Output>`
Blocks that also have a type and a name property:
    :py:class:`resource <p10s.terraform.Resource>`, and
    :py:class:`data <p10s.terraform.Data>`

Sometimes it's more convenient to start with hcl code, we can use the
:py:func:`from_hcl <p10s.terraform.from_hcl>` function:

.. code-block:: python

    c += tf.from_hcl(\"""
        resource "type" "name" {
          var = "value"
          ...
        }
    \""")

Note the hcl has two, equivalent, ways to assign a nested map (dict in python):

.. code-block:: none

    key {
       v = k
    }

and

.. code-block:: none

    key = {
       v = k
    }

When parsing hcl pyterranetes will convert both of these to a single
entry with key ``key`` and value a dict with the values of the
corresponsding block. As pyterranetes only actually generates
``.tf.json`` and not ``.tf`` (hcl) files, there is also no ambiguity
in the output.
"""

import json
from copy import deepcopy
from p10s.loads import hcl
from p10s.utils import merge_dicts
from p10s.context import BaseContext


class Context(BaseContext):
    """Context for terraform files.

As with the k8s.Context this instances of this class represent a
single terraform file. Block of terraform can be added using the
``+=`` operator.

    """
    output_file_extension = '.tf.json'

    def __init__(self, *args, data=None, **kwargs):
        if data is None:
            self.data = {}
        else:
            self.data = data

        super().__init__(*args, **kwargs)

    def _merge_in(self, values):
        self.data = merge_dicts(self.data, values)
        return self

    def add(self, block):
        if not isinstance(block, (list, tuple)):
            block = [block]
        for b in block:
            self._merge_in(b.data)
        return self

    def copy(self):
        return self.__class__(input=self.input, output=self.output, data=deepcopy(self.data))

    def __iadd__(self, block):
        """Add ``block`` to the context's data, destructively modifies ``self``

:param TerraformBlock block:
"""
        return self.add(block)

    def __add__(self, block):
        """Returns a new context containg all the data in ``self`` and ``block``

:param TerraformBlock block:
"""
        return self.copy().add(block)

    def render(self):
        with self.output.open("w") as tf_json:
            tf_json.write(json.dumps(self.data, indent=4, sort_keys=True))


class TerraformBlock():
    """Abstract base class for all terrform blocks.

Exposes the :py:meth:`.body <p10s.terrform.TerraformBlock.body>`
property for direct manipulation of the block's data.

    """
    def __init__(self, data=None):
        if data is not None:
            self.data = data

    def render(self):
        return self.data

    @property
    def body(self):
        """Returns the data contained in thie block. name, type, provider or
other non-body values are exposed as properties on the corresponding
object."""
        return self._body()

    def _body(self):
        raise NotImplementedError()


class NoArgsBlock(TerraformBlock):
    def __init__(self, body):
        super().__init__({
            self.KIND: body or {}
        })

    def copy(self):
        return self.__class__(body=deepcopy(self.body))

    def _body(self):
        return self.data[self.KIND]


class NameBlock(TerraformBlock):
    def __init__(self, name, body=None):
        self._name = name
        super().__init__({
            self.KIND: {
                name: body or {}
            }
        })

    def copy(self):
        return self.__class__(name=self.name, body=deepcopy(self.body))

    def _body(self):
        return self.data[self.KIND][self.name]

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if name != self._name:
            self.data[self.KIND][name] = self.data[self.KIND][self._name]
            del self.data[self.KIND][self._name]
            self._name = name


class TypeNameBlock(TerraformBlock):
    def __init__(self, type, name, body=None):
        self._type = type
        self._name = name
        super().__init__({
            self.KIND: {
                type: {
                    name: body or {}
                }
            }
        })

    def copy(self):
        return self.__class__(type=self.type, name=self.name, body=deepcopy(self.body))

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


class Locals(NoArgsBlock):
    KIND = 'locals'


class Variable(NameBlock):
    KIND = 'variable'


class Output(NameBlock):
    """``output`` block. Exposes `.name` as a property.

The constructor is designed to be convenient in p10s scripts and
accepts a number of parameters:

.. code-block:: python

    o = Output("ip", var_name="${aws_eip.ip.public_ip})

this simplified constructor works unless the variable you want to
define is named ``name`` or ``body``. if this every becomes a problem
in practice we'll see about removing the DIWM-ness.

and, of course, simpler construction works as well:

.. code-block:: python

    o = Output(name="ip", body={
        'var_name': "${aws_eip.ip.public_ip}
    })

    """
    KIND = 'output'

    def __init__(self, name=None, body=None, **kwargs):
        if name is None and body is None:
            keys = list(kwargs.keys())
            if len(keys) != 1:
                raise Exception("Output's dwim constructor expects exactly one arg, not %s", kwargs)
            name = keys[0]
            body = {
                'value': kwargs[name]
            }

        super().__init__(name=name, body=body)


class Module(NameBlock):
    """``module`` block. Exposes `.name` as a property."""
    KIND = 'module'


class Provider(NameBlock):
    """``provider`` block. Exposes `.name` as a property."""
    KIND = 'provider'


class Resource(TypeNameBlock):
    """``resource`` block. Exposes `.name` and `.type` as properties."""
    KIND = 'resource'


class Data(TypeNameBlock):
    """``data`` block. Exposes `.name` and `.type` as properties."""
    KIND = 'data'


def many_from_hcl(hcl_string):

    """Build TerraformBlock objects from hcl text. Always returns a list of blocks."""
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
                    cls = Locals
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


def from_hcl(hcl_string):
    """Build a TerraformBlock from hcl text:

:param hcl_string: hcl text to parse
:type hcl_string: a string, a pathlib.Path, or an io.Base object

.. code-block:: python

    c += tf.from_hcl(\"\"\"
      foo { }
    "\"\")

Note that the return value is an instance of tf.TerraformBlock, and
has all the corresponding methods:

.. code-block:: python

    resource = tf.from_hcl('''
      resource "type" "name" {
        key = 'value'
      }
    ''')

    resource.body['key'] = 'other value'

It can be convenient to keep most of the terraform code in a seperate
file and only use pyterranetes for certain operations. In this case
it's often best to leave the terraform code seperate and just read it
into the p10s script:

.. code-block:: python

    resource = tf.from_hcl(Path('./base.tf').open())

    for name in (name1, name2, ...):
        resource.name = name
        c += resource.copy()

    """
    blocks = many_from_hcl(hcl_string)

    if len(blocks) == 1:
        return blocks[0]
    else:
        raise Exception("Expected exactly one block when using `from_hcl` but got %s blocks from %s" %
                        (len(blocks), hcl_string))
