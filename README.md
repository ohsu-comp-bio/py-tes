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

```
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
```
