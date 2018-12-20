.. pyterranetes documentation master file, created by
   sphinx-quickstart on Tue Dec 11 22:45:21 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pyterranetes
============

``pyterranetes`` is a tool for managing the data files for terraform
and kubernetes/helm (or any other yaml or hcl based tools).

``pyterranetes`` has a different approach than most terranetes and k8s tools:

this is not a text based templating engine. instead you write python
code which creates plain python objects (dicts, list, strings,
numbers, etc.), these python objects are then serialized to proper
format (yaml, terraform json, etc.). 

Features:

- integrates cleanly into existing terraform and k8s code bases, it
  can be used as much, or as little, as needed.
- makes it easy to share code, conventions and values across both
  terraform and k8s.

.. toctree::
   :hidden:
   :maxdepth: 3
   :caption: Contents:

   installation
   tutorial
   invocation
   code-structure
   terraform
   kubernetes
   utilities
   indices
   
