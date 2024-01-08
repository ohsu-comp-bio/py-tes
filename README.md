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

> For backward compatibility and flexibility, `py-tes` is deliberately
> forgiving with respect to the path at which the TES API is hosted. It will
> try to locate the API by appending `/ga4gh/tes/v1` (standard location
> since TES v0.4.0) and `/v1` (standard location up to TES v0.3.0) to the host
> URL provided during client instantiation, in that order. To support TES APIs
> hosted at non-standard locations, `py-tes` will then try to locate the API at
> the provided host URL, without any suffix.  
>  
> Similarly, `py-tes` currently supports legacy TES implementations where the
> service info endpoint is hosted at `/tasks/service-info` (standard route up
> until TES 0.4.0) - if it does not find the endpoint at route `/service-info`
> (standard location since TES 0.5.0).  
>  
> Please note that this flexibility comes at cost: Up to six HTTP requests
> (accessing the service info via `/tasks/service-info` from a TES API at a
> non-standard location) may be necessary to locate the API. Therefore, if you
> are dealing with such TES services, you may need to increase the `timeout`
> duration (passed during client instantiation) beyond the default value of 10
> seconds.  
>  
> Please also consider asking your TES provider(s) to adopt the standard suffix
> and endpoint routes, as we may drop support for flexible API hosting in the
> future.

### How to...

For additional details, recipes and an API reference, read the
[docs](https://ohsu-comp-bio.github.io/py-tes).
