from __future__ import absolute_import, print_function

import re
import yaml

from requests import HTTPError
from tes.models import (Task, TaskParameter, Resources, Executor, Ports,
                        TaskLog, ExecutorLog, OutputFileLog)


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def camel_to_snake(name):
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()


def json2obj(j, o, convert_camel_case=True):
    if isinstance(j, str):
        m = yaml.safe_load(j)
    elif isinstance(j, dict):
        m = j
    else:
        raise TypeError("j must be a str or dict")

    d = {}
    if convert_camel_case:
        for k, v in m.items():
            d[camel_to_snake(k)] = v
    else:
        d = m

    omap = {
        "tasks": Task,
        "inputs": TaskParameter,
        "outputs": (TaskParameter, OutputFileLog),
        "logs": (TaskLog, ExecutorLog),
        "ports": Ports,
        "resources": Resources,
        "executors": Executor
    }

    def dict2obj(v, obj):
        if isinstance(v, list):
            field = []
            for item in v:
                field.append(obj(**item))
        else:
            field = obj(**v)
        return field

    r = {}
    for k, v in d.items():
        field = v
        if k in omap:
            if isinstance(omap[k], tuple):
                try:
                    obj = omap[k][0]
                    field = dict2obj(v, obj)
                except:
                    obj = omap[k][1]
                    field = dict2obj(v, obj)
            else:
                obj = omap[k]
                field = dict2obj(v, obj)
        r[k] = field

    return o(**r)


def raise_for_status(response):
    try:
        response.raise_for_status()
    except:
        raise HTTPError(
            "\n<status code> %d\n<response> %s\n" %
            (response.status_code, response.text)
        )
