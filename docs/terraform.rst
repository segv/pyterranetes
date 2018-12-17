Terraform
=========

Overview
--------

.. automodule:: p10s.terraform

Blocks
------

.. autoclass:: p10s.terraform.Resource
.. autoclass:: p10s.terraform.Data
.. autoclass:: p10s.terraform.Provider
.. autoclass:: p10s.terraform.Variable
.. autoclass:: p10s.terraform.Output
.. autoclass:: p10s.terraform.Locals
.. autoclass:: p10s.terraform.Module
.. autoclass:: p10s.terraform.Terraform

Helpers
-------

.. autofunction:: p10s.terraform.variables
.. autofunction:: p10s.terraform.outputs
.. autofunction:: p10s.terraform.from_hcl
.. autofunction:: p10s.terraform.many_from_hcl

Base Classes
------------

.. autoclass:: p10s.terraform.Context
   :members: copy, __add__, __iadd__
.. autoclass:: p10s.terraform.TerraformBlock
   :members:
