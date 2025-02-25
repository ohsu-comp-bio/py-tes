# py-tes 🐍

[![Build Status][build-badge]][build]
[![Test Coverage][coverage-badge]][coverage]
[![License][license-badge]][license]
[![PyPI][pypi-badge]][pypi]

[build-badge]: https://img.shields.io/github/actions/workflow/status/ohsu-comp-bio/py-tes/tests.yml?logo=github
[build]: https://github.com/ohsu-comp-bio/py-tes/actions
[coverage-badge]: https://coveralls.io/repos/github/ohsu-comp-bio/py-tes/badge.svg?branch=master
[coverage]: https://coveralls.io/github/ohsu-comp-bio/py-tes?branch=master
[license-badge]: https://img.shields.io/badge/License-MIT-yellow.svg
[license]: https://opensource.org/licenses/MIT
[pypi-badge]: https://img.shields.io/pypi/v/py-tes
[pypi]: https://pypi.org/project/py-tes/

_py-tes_ is a library for interacting with servers implementing the [GA4GH Task Execution Schema](https://github.com/ga4gh/task-execution-schemas).

# Quick Start ⚡

| TES version     | py-tes version + branch                             | Example Notebook (_Coming soon!_)           |
| --------------- | --------------------------------------------------- | ------------------------------------------- |
| [1.1][tes-v1.1] | [1.1.x][py-tes-v1.1] ([master][master])             | [![Open in Colab][colab-badge]][colab-v1.1] |
| [1.0][tes-v1.1] | [1.0.0][py-tes-v1.0] ([release/v1.0][release/v1.0]) | [![Open in Colab][colab-badge]][colab-v1.0] |

[master]: https://github.com/ohsu-comp-bio/py-tes/tree/master
[release/v1.0]: https://github.com/ohsu-comp-bio/py-tes/tree/release/v1.0
[tes-v1.1]: https://github.com/ga4gh/task-execution-schemas/releases/tag/v1.1
[tes-v1.0]: https://github.com/ga4gh/task-execution-schemas/releases/tag/v1.0
[py-tes-v1.1]: https://github.com/ohsu-comp-bio/py-tes/releases/latest
[py-tes-v1.0]: https://github.com/ohsu-comp-bio/py-tes/releases/tag/1.0.0
[colab-badge]: https://colab.research.google.com/assets/colab-badge.svg
[colab-v1.1]: https://colab.research.google.com/github/ohsu-comp-bio/py-tes/blob/master/examples/v1_1.ipynb
[colab-v1.0]: https://colab.research.google.com/github/ohsu-comp-bio/py-tes/blob/master/examples/v1_0.ipynb

# Install 🌀

Install `py-tes` from [PyPI](https://pypi.org/project/py-tes/) and run it in your script:

```sh
➜ pip install py-tes
```

# Quick Start ⚡

```py
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
```

# How to...

> Makes use of the objects above...

## ...export a model to a dictionary

```python
task_dict = task.as_dict(drop_empty=False)
```

`task_dict` contents:

```console
{'id': None, 'state': None, 'name': None, 'description': None, 'inputs': None, 'outputs': None, 'resources': None, 'executors': [{'image': 'alpine', 'command': ['echo', 'hello'], 'workdir': None, 'stdin': None, 'stdout': None, 'stderr': None, 'env': None}], 'volumes': None, 'tags': None, 'logs': None, 'creation_time': None}
```

## ...export a model to JSON

```python
task_json = task.as_json()  # also accepts `drop_empty` arg
```

`task_json` contents:

```console
{"executors": [{"image": "alpine", "command": ["echo", "hello"]}]}
```

## ...pretty print a model

```python
print(task.as_json(indent=3))  # keyword args are passed to `json.dumps()`
```

Output:

```json
{
  "executors": [
    {
      "image": "alpine",
      "command": ["echo", "hello"]
    }
  ]
}
```

## ...access a specific task from the task list

```py
specific_task = tasks_list.tasks[5]
```

`specific_task` contents:

```sh
Task(id='393K43', state='COMPLETE', name=None, description=None, inputs=None, outputs=None, resources=None, executors=None, volumes=None, tags=None, logs=None, creation_time=None)
```

## ...iterate over task list items

```py
for t in tasks_list[:3]:
    print(t.as_json(indent=3))
```

Output:

```sh
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
```

## ...instantiate a model from a JSON representation

```py
task_from_json = tes.client.unmarshal(task_json, tes.Task)
```

`task_from_json` contents:

```sh
Task(id=None, state=None, name=None, description=None, inputs=None, outputs=None, resources=None, executors=[Executor(image='alpine', command=['echo', 'hello'], workdir=None, stdin=None, stdout=None, stderr=None, env=None)], volumes=None, tags=None, logs=None, creation_time=None)
```

Which is equivalent to `task`:

```py
print(task_from_json == task)
```

Output:

```sh
True
```

# Credits

This project would not be possible without our collaborators at the University of Basel, Microsoft Research and AI, and the [The GA4GH Cloud Workstream](https://www.ga4gh.org/work_stream/cloud/) Team — thank you! 🙌

# Additional Resources 📚

- [ga4gh-sdk](https://github.com/elixir-cloud-aai/ga4gh-sdk): Generic SDK and CLI for GA4GH API services 

- [GA4GH TES](https://www.ga4gh.org/product/task-execution-service-tes/): Main page for the Task Execution Schema — a standardized schema and API for describing batch execution tasks.

- [TES GitHub](https://github.com/ga4gh/task-execution-schemas): Source repo for the Task Execution Schema

- [Awesome TES](https://github.com/ohsu-comp-bio/awesome-tes): A curated list of awesome GA4GH TES projects and programs
