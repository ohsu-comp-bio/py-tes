[![Build Status](https://travis-ci.org/ohsu-comp-bio/py-tes.svg?branch=master)](https://travis-ci.org/ohsu-comp-bio/py-tes)
[![Coverage Status](https://coveralls.io/repos/github/ohsu-comp-bio/py-tes/badge.svg?branch=master)](https://coveralls.io/github/ohsu-comp-bio/py-tes?branch=master)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

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

### Documentation

For additional details, recipes and an API reference, read the
[docs](https://ohsu-comp-bio.github.io/py-tes).
