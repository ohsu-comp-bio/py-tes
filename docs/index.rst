.. automodule:: tes

.. _manual-main:

======
py-tes
======

.. image:: https://travis-ci.org/ohsu-comp-bio/py-tes.svg?branch=master
    :target: https://travis-ci.org/ohsu-comp-bio/py-tes
.. image:: https://coveralls.io/repos/github/ohsu-comp-bio/py-tes/badge.svg?branch=master
    :target: https://coveralls.io/github/ohsu-comp-bio/py-tes?branch=master
.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT

*py-tes* is a library for interacting with servers implementing the
`GA4GH Task Execution
Schema <https://github.com/ga4gh/task-execution-schemas>`__.

Install
~~~~~~~

Available on `PyPI <https://pypi.org/project/py-tes/>`__.

::

   pip install py-tes

Example
~~~~~~~

::

   import tes

   task = tes.Task(
       executors=[
           tes.Executor(
               image="alpine",
               command=["echo", "hello"]
           )
       ]
   )

   cli = tes.HTTPClient("http://funnel.example.com", timeout=5)
   task_id = cli.create_task(task)
   res = cli.get_task(task_id)
   cli.cancel_task(task_id)


.. _main-support:

-------
Support
-------

* For releases, see :ref:`Changelog <changelog>`.
* Check :ref:`frequently asked questions (FAQ) <project_info-faq>`.
* For **bugs and feature requests**, please use the `issue tracker <https://github.com/ohsu-comp-bio/tes/issues>`_.
* For **contributions**, visit py-tes on `Github <https://github.com/ohsu-comp-bio/tes>`_ and read the :ref:`guidelines <project_info-contributing>`.

.. _main-resources:

---------
Resources
---------

`Snakemake Wrappers Repository <https://snakemake-wrappers.readthedocs.org>`_
    The Snakemake Wrapper Repository is a collection of reusable wrappers that allow to quickly use popular tools from Snakemake rules and workflows.

.. toctree::
   :caption: API
   :name: api_docs
   :hidden:
   :maxdepth: 1

   api_docs/tes
