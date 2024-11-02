# py-tes 🐍

[![GitHub Actions Test Status](https://img.shields.io/github/actions/workflow/status/ohsu-comp-bio/py-tes/tests.yml?logo=github)](https://github.com/ohsu-comp-bio/py-tes/actions) [![image](https://coveralls.io/repos/github/ohsu-comp-bio/py-tes/badge.svg?branch=master)](https://coveralls.io/github/ohsu-comp-bio/py-tes?branch=master) [![image](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*py-tes* is a library for interacting with servers implementing the
[GA4GH Task Execution
Schema](https://github.com/ga4gh/task-execution-schemas).

## Install ⚡

Available on [PyPI](https://pypi.org/project/py-tes/).

    pip install py-tes

## Example ✍️


``` python
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
```

## How to...

> Makes use of the objects above...

### ...export a model to a dictionary

``` python
task_dict = task.as_dict(drop_empty=False)
```

`task_dict` contents:

``` console
{'id': None, 'state': None, 'name': None, 'description': None, 'inputs': None, 'outputs': None, 'resources': None, 'executors': [{'image': 'alpine', 'command': ['echo', 'hello'], 'workdir': None, 'stdin': None, 'stdout': None, 'stderr': None, 'env': None}], 'volumes': None, 'tags': None, 'logs': None, 'creation_time': None}
```

### ...export a model to JSON

``` python
task_json = task.as_json()  # also accepts `drop_empty` arg
```

`task_json` contents:

``` console
{"executors": [{"image": "alpine", "command": ["echo", "hello"]}]}
```

### ...pretty print a model

``` python
print(task.as_json(indent=3))  # keyword args are passed to `json.dumps()`
```

Output:

``` json
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
```

### ...access a specific task from the task list

``` python
specific_task = tasks_list.tasks[5]
```

`specific_task` contents:

``` console
Task(id='393K43', state='COMPLETE', name=None, description=None, inputs=None, outputs=None, resources=None, executors=None, volumes=None, tags=None, logs=None, creation_time=None)
```

### ...iterate over task list items

``` python
for t in tasks_list[:3]:
    print(t.as_json(indent=3))
```

Output:

``` console
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

### ...instantiate a model from a JSON representation

``` python
task_from_json = tes.client.unmarshal(task_json, tes.Task)
```

`task_from_json` contents:

``` console
Task(id=None, state=None, name=None, description=None, inputs=None, outputs=None, resources=None, executors=[Executor(image='alpine', command=['echo', 'hello'], workdir=None, stdin=None, stdout=None, stderr=None, env=None)], volumes=None, tags=None, logs=None, creation_time=None)
```

Which is equivalent to `task`:

``` python
print(task_from_json == task)
```

Output:

``` console
True
```

## Additional Resources 📚

- [ga4gh-tes](https://github.com/microsoft/ga4gh-tes) : C# implementation of the GA4GH TES API; provides distributed batch task execution on Microsoft Azure

- [cwl-tes](https://github.com/ohsu-comp-bio/cwl-tes) : cwl-tes submits your tasks to a TES server. Task submission is parallelized when possible.

- [Funnel](https://ohsu-comp-bio.github.io/funnel/): Funnel is a toolkit for distributed task execution with a simple API.

- [Snakemake](https://snakemake.github.io/) : The Snakemape workflow management system is a tool to create reproducible and scalable data analyses

- [Nextflow](https://www.nextflow.io/): Nextflow enables scalable and reproducible scientific workflows using software containers. It allows the adaptation of pipelines written in the most common scripting languages.

- [GA4GH TES](https://www.ga4gh.org/product/task-execution-service-tes/): Main page for the Task Execution Schema — a standardized schema and API for describing batch execution tasks. 

- [TES GitHub](https://github.com/ga4gh/task-execution-schemas): Source repo for the Task Execution Schema 
