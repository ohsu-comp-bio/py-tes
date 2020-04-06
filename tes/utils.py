from __future__ import absolute_import, print_function, unicode_literals

import json
import re

from requests import HTTPError
from tes.models import (Task, Input, Output, Resources, Executor,
                        TaskLog, ExecutorLog, OutputFileLog)


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def camel_to_snake(name):
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()


class UnmarshalError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class TimeoutError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


def unmarshal(j, o, convert_camel_case=True):
    if isinstance(j, str):
        m = json.loads(j)
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
        "inputs": Input,
        "outputs": (Output, OutputFileLog),
        "logs": (ExecutorLog, TaskLog),
        "resources": Resources,
        "executors": Executor
    }

    def _unmarshal(v, obj):
        if isinstance(v, list):
            field = []
            for item in v:
                field.append(unmarshal(item, obj))
        else:
            field = unmarshal(v, obj)
        return field

    r = {}
    for k, v in d.items():
        field = v
        if k in omap:
            if isinstance(omap[k], tuple):
                try:
                    obj = omap[k][0]
                    field = _unmarshal(v, obj)
                except Exception:
                    obj = omap[k][1]
                    field = _unmarshal(v, obj)
            else:
                obj = omap[k]
                field = _unmarshal(v, obj)
        r[k] = field

    try:
        output = o(**r)
    except Exception as e:
        msg = "%s could not be unmarshalled to type: %s" % (j, o.__name__) + \
              "\n" + \
              "%s: %s" % (type(e).__name__, e)
        raise UnmarshalError(msg)

    return output


def raise_for_status(response):
    try:
        response.raise_for_status()
    except Exception:
        raise HTTPError(
            "\n<status code> %d\n<response> %s\n" %
            (response.status_code, response.text)
        )
