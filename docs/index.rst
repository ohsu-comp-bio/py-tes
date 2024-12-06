py-tes 🐍
========

.. image:: https://img.shields.io/github/actions/workflow/status/ohsu-comp-bio/py-tes/tests.yml?logo=github
   :target: https://github.com/ohsu-comp-bio/py-tes/actions
   :alt: Build Status

.. image:: https://coveralls.io/repos/github/ohsu-comp-bio/py-tes/badge.svg?branch=master
   :target: https://coveralls.io/github/ohsu-comp-bio/py-tes?branch=master
   :alt: Test Coverage

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License

.. image:: https://img.shields.io/pypi/v/py-tes
   :target: https://pypi.org/project/py-tes/
   :alt: PyPI

*py-tes* is a library for interacting with servers implementing the `GA4GH Task Execution Schema <https://github.com/ga4gh/task-execution-schemas>`_.

Quick Start ⚡
-------------

.. list-table::
   :header-rows: 1

   * - TES version
     - py-tes version
     - Example Notebook (*Coming soon!*)
   * - `1.1 <https://github.com/ga4gh/task-execution-schemas/releases/tag/v1.1>`_
     - `1.1.0 <https://github.com/ohsu-comp-bio/py-tes/releases/tag/1.1.0>`_
     - `Open in Colab <https://colab.research.google.com/github/ohsu-comp-bio/py-tes/blob/develop/examples/v1_1_0.ipynb>`_
   * - `1.0 <https://github.com/ga4gh/task-execution-schemas/releases/tag/v1.0>`_
     - `1.0.0 <https://github.com/ohsu-comp-bio/py-tes/releases/tag/1.0.0>`_
     - `Open in Colab <https://colab.research.google.com/github/ohsu-comp-bio/py-tes/blob/develop/examples/v1_0_0.ipynb>`_

Installation 🌀
---------------

Install ``py-tes`` from `PyPI <https://pypi.org/project/py-tes/>`_ and run it in your script:

.. code-block:: console

    ➜ pip install py-tes

    ➜ python example.py

Example
-------

.. code-block:: python

    import tes
    import json

    # Define task
    task = tes.Task(
        executors=[
            tes.Executor(
                image="alpine",
                command=["echo", "hello"]
            )
        ]
    )

    # Create client
    cli = tes.HTTPClient("http://localhost:8000", timeout=5)

    # Create and run task
    task_id = cli.create_task(task)
    cli.wait(task_id, timeout=5)

    # Fetch task info
    task_info = cli.get_task(task_id, view="BASIC")
    j = json.loads(task_info.as_json())

    # Pretty print task info
    print(json.dumps(j, indent=2))

How to...
---------

> The following examples make use of the objects above.

...export a model to a dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    task_dict = task.as_dict(drop_empty=False)

`task_dict` contents:

.. code-block:: json

    {
        "id": null,
        "state": null,
        ...
    }

...export a model to JSON
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    task_json = task.as_json()  # also accepts `drop_empty` arg

`task_json` contents:

.. code-block:: json

    {"executors": [{"image": "alpine", "command": ["echo", "hello"]}]}

...pretty print a model
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    print(task.as_json(indent=3))  # keyword args are passed to `json.dumps()`

Output:

.. code-block:: json

    {
        "executors": [
            {
                "image": "alpine",
                "command": ["echo", "hello"]
            }
        ]
    }

...access a specific task from the task list
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    specific_task = tasks_list.tasks[5]

`specific_task` contents:

.. code-block:: console

    Task(id='393K43', state='COMPLETE', ...)

...iterate over task list items
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    for t in tasks_list[:3]:
        print(t.as_json(indent=3))

Output:

.. code-block:: console

    {
        "id": "task_A2GFS4",
        "state": "RUNNING"
    }
    ...

...instantiate a model from a JSON representation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    task_from_json = tes.client.unmarshal(task_json, tes.Task)

`task_from_json` contents:

.. code-block:: console

    Task(id=None, state=None, ...)

Which is equivalent to `task`:

.. code-block:: python

    print(task_from_json == task)

Output:

.. code-block:: console

    True

Additional Resources 📚
------------------------

- `ga4gh-tes <https://github.com/microsoft/ga4gh-tes>`_ : C# implementation of the GA4GH TES API; provides distributed batch task execution on Microsoft Azure
- `cwl-tes <https://github.com/ohsu-comp-bio/cwl-tes>`_ : Submits tasks to a TES server.
- `Funnel <https://ohsu-comp-bio.github.io/funnel/>`_ : Toolkit for distributed task execution with a simple API.
- `Snakemake <https://snakemake.github.io/>`_ : Workflow management system.
- `Nextflow <https://www.nextflow.io/>`_ : Scalable and reproducible workflows using containers.
- `GA4GH TES <https://www.ga4gh.org/product/task-execution-service-tes/>`_ : Standardized schema and API for batch execution tasks.
- `TES GitHub <https://github.com/ga4gh/task-execution-schemas>`_
- `Awesome TES <https://github.com/ohsu-comp-bio/awesome-tes>`_ : A curated list of TES projects.
