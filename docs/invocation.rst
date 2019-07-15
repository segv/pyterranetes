Invocation
==========

To generate output from p10s scripts just run p10s and specify where
the scripts are locateed:

.. code-block:: bash

    $ p10s generate .

All p10s sub commands can be shortened to uniqeness, and the default
directory for ``generate`` is ``.``, so the above is equivalent to:

.. code-block:: bash

    $ p10s g

The ``watch`` sub command can be used to automatically generate any
p10s modified or created in a particular dir:

.. code-block:: bash

    $ p10s watch .
    ...
    ^C
    $

Very (very) often we want to run `terraform` or `kubectl` after having
run p10s, so these two CLIs have convenience commands in p10s allowing
one to do this:

.. code-block:: bash

    $ p10s terraform plan


which will first run `generate` in the current directory and then call
`terraform plan`, instead of this:

.. code-block:: bash

    $ p10s generate && terraform plan

There is an analogous short cut for `kubectl`.  instead of this:
