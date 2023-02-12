import json
import re

from typing import Any, Dict, Type

from tes.models import (Task, Input, Output, Resources, Executor,
                        TaskLog, ExecutorLog, OutputFileLog)


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def camel_to_snake(name: str) -> str:
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()


class UnmarshalError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class TimeoutError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


def unmarshal(j: Any, o: Type, convert_camel_case=True) -> Any:
    m: Any = None
    if isinstance(j, str):
        try:
            m = json.loads(j)
        except json.decoder.JSONDecodeError:
            pass
    elif j is None:
        return None
    else:
        m = j

    if not isinstance(m, dict):
        raise TypeError("j must be a dictionary, a JSON string evaluation to "
                        "a dictionary, or None")

    d: Dict[str, Any] = {}
    if convert_camel_case:
        for k, v in m.items():
            d[camel_to_snake(k)] = v
    else:
        d = m

    fullOmap = {
        "Executor": {
            "logs": ExecutorLog
        },
        "Task": {
            "logs": TaskLog,
            "inputs": Input,
            "outputs": Output,
            "resources": Resources,
            "executors": Executor
        },
        "TaskLog": {
            "outputs": OutputFileLog,
            "logs": ExecutorLog
        },
        "ListTasksResponse": {
            "tasks": Task,
        }
    }

    def _unmarshal(v: Any, obj: Type) -> Any:
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
        omap = fullOmap.get(o.__name__, {})
        if k in omap:
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
