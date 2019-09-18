.. pyterranetes documentation master file, created by
   sphinx-quickstart on Tue Dec 11 22:45:21 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pyterranetes
============

What is it?
-----------

``pyterranetes`` is a tool for managing the data files for terraform
and kubernetes/helm (or any other yaml or hcl based tools).

``pyterranetes`` integrates cleanly into existing terraform and k8s
code bases, it can be used as much, or as little, as needed.

Since ``pyterranetes`` is just python, and since it knows how to
generate both terraform configs and kubernetes yaml, it makes it easy
to share code and values across both tools.

``pyterranetes`` has a different approach than most terranetes and k8s
wrappers: in particular ``pyterranetes`` is not a text based
templating engine. instead you write python code which creates plain
python objects (dicts, list, strings, numbers, etc.), these python
objects are then serialized to proper format (yaml, terraform json,
etc.).

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
   config
   utilities
   appendix
