py-tes
======

_py-tes_ is a library for interacting with servers implementing the [GA4GH Task Execution Schema](https://github.com/ga4gh/task-execution-schemas).


### Install

Available on [PyPI](https://pypi.org/project/py-tes/).

```
pip install py-tes
```

### Example

```python
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

### How to...

> Makes use of the objects above...

#### ...export a model to a dictionary

```python
task_dict = task.as_dict(drop_empty=False)
```

`task_dict` contents:

```console
{'id': None, 'state': None, 'name': None, 'description': None, 'inputs': None, 'outputs': None, 'resources': None, 'executors': [{'image': 'alpine', 'command': ['echo', 'hello'], 'workdir': None, 'stdin': None, 'stdout': None, 'stderr': None, 'env': None}], 'volumes': None, 'tags': None, 'logs': None, 'creation_time': None}
```

#### ...export a model to JSON

```python
task_json = task.as_json()  # also accepts `drop_empty` arg
```

`task_json` contents:

```console
{"executors": [{"image": "alpine", "command": ["echo", "hello"]}]}
```

#### ...pretty print a model

```python
print(task.as_json(indent=3))  # keyword args are passed to `json.dumps()`
```

Output:

```json
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

#### ...access a specific task from the task list

```python
specific_task = tasks_list.tasks[5]
```

`specific_task` contents:

```console
Task(id='393K43', state='COMPLETE', name=None, description=None, inputs=None, outputs=None, resources=None, executors=None, volumes=None, tags=None, logs=None, creation_time=None)
```

#### ...iterate over task list items

```python
for t in tasks_list[:3]:
    print(t.as_json(indent=3))
```

Output:

```console
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

#### ...instantiate a model from a JSON representation

```python
task_from_json = tes.client.unmarshal(task_json, tes.Task)
```

`task_from_json` contents:

```console
Task(id=None, state=None, name=None, description=None, inputs=None, outputs=None, resources=None, executors=[Executor(image='alpine', command=['echo', 'hello'], workdir=None, stdin=None, stdout=None, stderr=None, env=None)], volumes=None, tags=None, logs=None, creation_time=None)
```

Which is equivalent to `task`:

```python
print(task_from_json == task)
```

Output:

```console
True
```
