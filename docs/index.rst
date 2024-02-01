.. automodule:: tes

.. _manual-main:

======
py-tes
======

.. image:: https://img.shields.io/github/actions/workflow/status/ohsu-comp-bio/py-tes/tests.yml?logo=github
   :alt: GitHub Actions Test Status
   :target: https://github.com/ohsu-comp-bio/py-tes/actions
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

.. code:: python

   import tes

   # define task
   task = tes.Task(
       executors=[
           tes.Executor(
               image="alpine",
               command=["echo", "hello"]
           )
       ]
   )

   # create client
   cli = tes.HTTPClient("https://funnel.example.com", timeout=5)

   # access endpoints
   service_info = cli.get_service_info()
   task_id = cli.create_task(task)
   task_info = cli.get_task(task_id, view="BASIC")
   cli.cancel_task(task_id)
   tasks_list = cli.list_tasks(view="MINIMAL")  # default view

How to…
~~~~~~~

   Makes use of the objects above…

…export a model to a dictionary
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

   task_dict = task.as_dict(drop_empty=False)

``task_dict`` contents:

.. code:: console

   {'id': None, 'state': None, 'name': None, 'description': None, 'inputs': None, 'outputs': None, 'resources': None, 'executors': [{'image': 'alpine', 'command': ['echo', 'hello'], 'workdir': None, 'stdin': None, 'stdout': None, 'stderr': None, 'env': None}], 'volumes': None, 'tags': None, 'logs': None, 'creation_time': None}

…export a model to JSON
^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

   task_json = task.as_json()  # also accepts `drop_empty` arg

``task_json`` contents:

.. code:: console

   {"executors": [{"image": "alpine", "command": ["echo", "hello"]}]}

…pretty print a model
^^^^^^^^^^^^^^^^^^^^^

.. code:: python

   print(task.as_json(indent=3))  # keyword args are passed to `json.dumps()`

Output:

.. code:: json

   {
      "executors": [
         {
            "image": "alpine",
            "command": [
               "echo",
               "hello"
            ]
         }
      ]
   }

…access a specific task from the task list
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

   specific_task = tasks_list.tasks[5]

``specific_task`` contents:

.. code:: console

   Task(id='393K43', state='COMPLETE', name=None, description=None, inputs=None, outputs=None, resources=None, executors=None, volumes=None, tags=None, logs=None, creation_time=None)

…iterate over task list items
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

   for t in tasks_list[:3]:
       print(t.as_json(indent=3))

Output:

.. code:: console

   {
      "id": "task_A2GFS4",
      "state": "RUNNING"
   }
   {
      "id": "task_O8G1PZ",
      "state": "CANCELED"
   }
   {
      "id": "task_W246I6",
      "state": "COMPLETE"
   }

…instantiate a model from a JSON representation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

   task_from_json = tes.client.unmarshal(task_json, tes.Task)

``task_from_json`` contents:

.. code:: console

   Task(id=None, state=None, name=None, description=None, inputs=None, outputs=None, resources=None, executors=[Executor(image='alpine', command=['echo', 'hello'], workdir=None, stdin=None, stdout=None, stderr=None, env=None)], volumes=None, tags=None, logs=None, creation_time=None)

Which is equivalent to ``task``:

.. code:: python

   print(task_from_json == task)

Output:

.. code:: console

   True

.. _main-support:

Support
~~~~~~~

* For releases, see :ref:`Changelog <changelog>`.
* Check :ref:`frequently asked questions (FAQ) <project_info-faq>`.
* For **bugs and feature requests**, please use the `issue tracker <https://github.com/ohsu-comp-bio/tes/issues>`_.
* For **contributions**, visit py-tes on `Github <https://github.com/ohsu-comp-bio/py-tes>`_

.. _main-resources:

Resources
~~~~~~~~~

`cwl-tes <https://github.com/ohsu-comp-bio/cwl-tes>`_
    cwl-tes submits your tasks to a TES server. Task submission is parallelized when possible. 

`Funnel <https://ohsu-comp-bio.github.io/funnel/>`_
    Funnel is a toolkit for distributed task execution with a simple API.

`ga4gh-tes <https://github.com/microsoft/ga4gh-tes>`_
    C# implementation of the GA4GH TES API; provides distributed batch task execution on Microsoft Azure 

`Nextflow <https://www.nextflow.io/>`_
    Nextflow enables scalable and reproducible scientific workflows using software containers. It allows the adaptation of pipelines written in the most common scripting languages. 

`Snakemake <https://snakemake.github.io/>`_
    The Snakemape workflow management system is a tool to create reproducible and scalable data analyses

.. toctree::
   :caption: API
   :name: api
   :hidden:
   :maxdepth: 1

   api/tes
