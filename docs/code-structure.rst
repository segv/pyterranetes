Code Structure
==============
    
Sharing Code
------------

To make it easier to share functions and code across scripts p10s will
automatically add any directory named ``pyterranetes`` in the file
system hierarchy, relative to the p10s script begin processed, to
``PYTHONPATH``.

Generally you'd have a project structure like this:

.. code-block:: none

  root/
    pyterranetes/
      project.py
    terraform/
      values.yaml
      web/
        main.p10s
      db/
        main.p10s

and in your ``.p10s`` scripts you'd include your common code with a simple import:

.. code-block:: python

    import project


The ``p10s`` module
-------------------

.. automodule:: p10s
