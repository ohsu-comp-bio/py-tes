from __future__ import absolute_import, print_function

import json

from attr import asdict, attrs, attrib
from attr.validators import instance_of, optional, in_


@attrs
class _ListOfValidator(object):
    type = attrib()

    def __call__(self, inst, attr, value):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        if not all([isinstance(n, self.type) for n in value]):
            raise TypeError(
                "'{name}' must be a list of {type!r} (got {value!r} that is a "
                "list of {actual!r})."
                .format(name=attr.name,
                        type=self.type,
                        actual=value[0].__class__,
                        value=value),
                attr, self.type, value,
            )

    def __repr__(self):
        return (
            "<instance_of validator for type {type!r}>"
            .format(type=self.type)
        )


def list_of(type):
    return _ListOfValidator(type)


def _drop_none(obj):
    if isinstance(obj, (list, tuple, set)):
        return type(obj)(_drop_none(x) for x in obj if x is not None)
    elif isinstance(obj, dict):
        return type(obj)(
            (_drop_none(k), _drop_none(v))
            for k, v in obj.items() if k is not None and v is not None
        )
    else:
        return obj


@attrs
class Base(object):

    def as_dict(self, drop_empty=True):
        obj = asdict(self)
        if drop_empty:
                return _drop_none(obj)
        return obj

    def as_json(self, drop_empty=True):
        return json.dumps(
            self.as_dict(drop_empty)
        )


@attrs
class TaskParameter(Base):
    url = attrib(
        default=None, validator=optional(instance_of((str, unicode)))
    )
    path = attrib(
        default=None, validator=optional(instance_of((str, unicode)))
    )
    type = attrib(
        default="FILE", validator=in_(["FILE", "DIRECTORY"])
    )
    name = attrib(
        default=None, validator=optional(instance_of((str, unicode)))
    )
    description = attrib(
        default=None, validator=optional(instance_of((str, unicode)))
    )
    contents = attrib(
        default=None, validator=optional(instance_of((str, unicode)))
    )


@attrs
class Resources(Base):
    cpu_cores = attrib(
        default=None, validator=optional(instance_of(int))
    )
    ram_gb = attrib(
        default=None, validator=optional(instance_of((float, int)))
    )
    size_gb = attrib(
        default=None, validator=optional(instance_of((float, int)))
    )
    preemptible = attrib(
        default=None, validator=optional(instance_of(bool))
    )
    zones = attrib(
        default=None, validator=optional(list_of((str, unicode)))
    )


@attrs
class Ports(Base):
    container = attrib(validator=instance_of(int))
    host = attrib(default=0, validator=instance_of(int))


@attrs
class Executor(Base):
    image_name = attrib(
        validator=instance_of((str, unicode))
    )
    cmd = attrib(
        validator=list_of((str, unicode))
    )
    work_dir = attrib(
        default=None, validator=optional(instance_of((str, unicode)))
    )
    stdin = attrib(
        default=None, validator=optional(instance_of((str, unicode)))
    )
    stdout = attrib(
        default=None, validator=optional(instance_of((str, unicode)))
    )
    stderr = attrib(
        default=None, validator=optional(instance_of((str, unicode)))
    )
    ports = attrib(
        default=None, validator=optional(list_of(Ports))
    )
    environ = attrib(
        default=None, validator=optional(instance_of(dict))
    )


@attrs
class ExecutorLog(Base):
    start_time = attrib(
        default=None, validator=optional(instance_of((str, unicode)))
    )
    end_time = attrib(
        default=None, validator=optional(instance_of((str, unicode)))
    )
    stdout = attrib(
        default=None, validator=optional(instance_of((str, unicode)))
    )
    stderr = attrib(
        default=None, validator=optional(instance_of((str, unicode)))
    )
    exit_code = attrib(
        default=None, validator=optional(instance_of(int))
    )
    host_ip = attrib(
        default=None, validator=optional(instance_of((str, unicode)))
    )
    ports = attrib(
        default=None, validator=optional(list_of(Ports))
    )


@attrs
class OutputFileLog(Base):
    url = attrib(
        validator=instance_of((str, unicode))
    )
    path = attrib(
        validator=instance_of((str, unicode))
    )
    size_bytes = attrib(
        validator=instance_of(int)
    )


@attrs
class TaskLog(Base):
    start_time = attrib(
        default=None, validator=optional(instance_of((str, unicode)))
    )
    end_time = attrib(
        default=None, validator=optional(instance_of((str, unicode)))
    )
    metadata = attrib(
        default=None, validator=optional(instance_of(dict))
    )
    logs = attrib(
        default=None, validator=optional(list_of(ExecutorLog))
    )
    outputs = attrib(
        default=None, validator=optional(list_of(OutputFileLog))
    )


@attrs
class Task(Base):
    id = attrib(
        default=None, validator=optional(instance_of((str, unicode)))
    )
    state = attrib(
        default=None,
        validator=optional(in_(
            ["UKNOWN", "QUEUED", "INITIALIZING", "RUNNING", "COMPLETE",
             "PAUSED", "CANCELED", "ERROR", "SYSTEM_ERROR"]
        ))
    )
    name = attrib(
        default=None, validator=optional(instance_of((str, unicode)))
    )
    project = attrib(
        default=None, validator=optional(instance_of((str, unicode)))
    )
    description = attrib(
        default=None, validator=optional(instance_of((str, unicode)))
    )
    inputs = attrib(
        default=None, validator=optional(list_of(TaskParameter))
    )
    outputs = attrib(
        default=None, validator=optional(list_of(TaskParameter))
    )
    resources = attrib(
        default=None, validator=optional(instance_of(Resources))
    )
    executors = attrib(
        default=None, validator=optional(list_of(Executor))
    )
    volumes = attrib(
        default=None, validator=optional(list_of((str, unicode)))
    )
    tags = attrib(
        default=None, validator=optional(instance_of(dict))
    )
    logs = attrib(
        default=None, validator=optional(list_of(TaskLog))
    )

    def is_valid(self):
        if self.executors is None:
            return False, TypeError("executors NoneType")
        else:
            for e in self.executors:
                if e.environ is not None:
                    for k, v in self.executors.environ:
                        if not isinstance(k, str) and not isinstance(k, str):
                            return False, TypeError(
                                "keys and values of environ must be StrType"
                            )

        if self.inputs is not None:
            for i in self.inputs:
                if i.url is None and i.contents is None:
                    return False, TypeError(
                        "TaskParameter url must be provided"
                    )
                if i.url is not None and i.contents is not None:
                    return False, TypeError(
                        "TaskParameter url and contents are mutually exclusive"
                    )
                if i.url is None and i.path is None:
                    return False, TypeError(
                        "TaskParameter url and path must be provided"
                    )

        if self.outputs is not None:
            for o in self.outputs:
                if o.url is None or o.path is None:
                    return False, TypeError(
                        "TaskParameter url and path must be provided"
                    )
                if o.contents is not None:
                    return False, TypeError(
                        "Output TaskParameter instances do not have contents"
                    )
        return True, None


@attrs
class GetTaskRequest(Base):
    id = attrib(
        validator=instance_of((str, unicode))
    )
    view = attrib(
        default=None, validator=optional(in_(["MINIMAL", "BASIC", "FULL"]))
    )


@attrs
class CreateTaskResponse(Base):
    id = attrib(
        validator=instance_of((str, unicode))
    )


@attrs
class ServiceInfoRequest(Base):
    pass


@attrs
class ServiceInfo(Base):
    name = attrib(
        default=None, validator=optional(instance_of((str, unicode)))
    )
    doc = attrib(
        default=None, validator=optional(instance_of((str, unicode)))
    )
    storage = attrib(
        default=None, validator=optional(list_of((str, unicode)))
    )


@attrs
class CancelTaskRequest(Base):
    id = attrib(
        validator=instance_of((str, unicode))
    )


@attrs
class CancelTaskResponse(Base):
    pass


@attrs
class ListTasksRequest(Base):
    project = attrib(
        default=None, validator=optional(instance_of((str, unicode)))
    )
    name_prefix = attrib(
        default=None, validator=optional(instance_of((str, unicode)))
    )
    page_size = attrib(
        default=None, validator=optional(instance_of(int))
    )
    page_token = attrib(
        default=None, validator=optional(instance_of((str, unicode)))
    )
    view = attrib(
        default=None, validator=optional(in_(["MINIMAL", "BASIC", "FULL"]))
    )


@attrs
class ListTasksResponse(Base):
    tasks = attrib(
        validator=list_of(Task)
    )
    next_page_token = attrib(
        default=None, validator=optional(instance_of((str, unicode)))
    )
