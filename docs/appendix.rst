Appendix
========

Other Tools Solving This Problem
--------------------------------

- `terraboot <https://github.com/MastodonC/terraboot>`_ lisp like syntax which compiles to terraform.
- `terragrunt <https://github.com/gruntwork-io/terragrunt>`_ framework/conventions for reducing duplication in terraform code. opinionated.
- `tfscaffold <https://github.com/tfutils/tfscaffold>`_ not totally different from terragrunt. framework/conventions for dealing with a matrix of configs in terraform.
- `jsonnet <https://jsonnet.org/>`_ language for generating json which is popular(-ish) in terraform/k8s projects.
- `kadet <https://github.com/deepmind/kapitan/blob/master/kapitan/inputs/kadet.py>`_ python based config management for k8s. not totally different from pyterranetes.

``pyterranetes`` vs X
----------------------------------------------

Compared to plain terraform
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most of the advantages of pyterranetes come from using a general
purpose programming language (code) to generate terraform instead of
having to write out the config (data) by hand.

- It is easy to write simple python functions which create large
  number of resources (modules, providers, data, outputs, etc.), with
  arbitrary changes to the values. Managing mutiple environments (qa,
  staging, integration, prod, etc.) can be done easily without copy 'n
  pasting provider, and module and output blocks:

  .. code-block:: python

      content += [generate_tf_config(app) for app in MY_APPS]

- These same functions enforce whatever local conventions yoru team
  has. Instead of keeping conventions in the docs we can build the
  conventions into our config code diectly.

    .. code-block:: python

      def a_resource(name):
        if not re.match(r'(stg|prd|qa)_\d+', name):
          raise Error("Invalid name %s" % name)
        ...

- values can be retreived from any source that python can talk to,
  beyond what's available or convenient as a terrafor provider (local
  yaml files, databases, etc.)
  
  .. code-block:: python

      VALUES = Values.from_files(__file__)
      context += [make_db_module(db) for db in VALUES['dbs']]

- While ``pyterranetes`` does not impose its own organization or
  conventions on top of terraform (unlike, for example, `terragrunt
  <https://github.com/gruntwork-io/terragrunt>`_ or `tfscaffold
  <https://github.com/tfutils/tfscaffold>`_) it provides you with the
  tools needed to build the conventions that fit best in your env.

Compared to plain kubernetes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As with terraform the primary advantage here is that we can write
python functions, as opposed to copy 'n paste or simple go templates,
to generate the kubernetes taml files even across charts or apps.

while ``pyterranetes`` doesn't have any explicit support for `helm
<https://helm.sh/>`_ being able to produce helm (or helmfile) yaml is
all that's been needed so far.

  
Search
------

:ref:`search`

Index
-----

:ref:`genindex`
