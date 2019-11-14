from __future__ import absolute_import, print_function, unicode_literals

import dateutil.parser
import json
import os
import six

from attr import asdict, attrs, attrib
from attr.validators import instance_of, optional, in_
from builtins import str
from datetime import datetime


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


def strconv(value):
    if isinstance(value, (tuple, list)):
        if all([isinstance(n, six.string_types) for n in value]):
            return [str(n) for n in value]
        else:
            return value
    elif isinstance(value, six.string_types):
        return str(value)
    else:
        return value


# since an int64 value is encoded as a string in json we need to handle
# conversion
def int64conv(value):
    if value is not None:
        return int(value)
    return value


def timestampconv(value):
    if isinstance(value, six.string_types):
        return dateutil.parser.parse(value)
    return value


def datetime_json_handler(x):
    if isinstance(x, datetime):
        return x.isoformat()
    raise TypeError("Unknown type")


@attrs
class Base(object):

    def as_dict(self, drop_empty=True):
        obj = asdict(self)
        if drop_empty:
            return _drop_none(obj)
        return obj

    def as_json(self, drop_empty=True):
        return json.dumps(
            self.as_dict(drop_empty),
            default=datetime_json_handler
        )


@attrs
class Input(Base):
    url = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    path = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    type = attrib(
        default="FILE", validator=in_(["FILE", "DIRECTORY"])
    )
    name = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    description = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    content = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )


@attrs
class Output(Base):
    url = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    path = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    type = attrib(
        default="FILE", validator=in_(["FILE", "DIRECTORY"])
    )
    name = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    description = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )


@attrs
class Resources(Base):
    cpu_cores = attrib(
        default=None, validator=optional(instance_of(int))
    )
    ram_gb = attrib(
        default=None, validator=optional(instance_of((float, int)))
    )
    disk_gb = attrib(
        default=None, validator=optional(instance_of((float, int)))
    )
    preemptible = attrib(
        default=None, validator=optional(instance_of(bool))
    )
    zones = attrib(
        default=None, converter=strconv, validator=optional(list_of(str))
    )


@attrs
class Executor(Base):
    image = attrib(
        converter=strconv, validator=instance_of(str)
    )
    command = attrib(
        converter=strconv, validator=list_of(str)
    )
    workdir = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    stdin = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    stdout = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    stderr = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    env = attrib(
        default=None, validator=optional(instance_of(dict))
    )


@attrs
class ExecutorLog(Base):
    start_time = attrib(
        default=None,
        converter=timestampconv,
        validator=optional(instance_of(datetime))
    )
    end_time = attrib(
        default=None,
        converter=timestampconv,
        validator=optional(instance_of(datetime))
    )
    stdout = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    stderr = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    exit_code = attrib(
        default=None, validator=optional(instance_of(int))
    )


@attrs
class OutputFileLog(Base):
    url = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    path = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    size_bytes = attrib(
        default=None, converter=int64conv, validator=optional(instance_of(int))
    )


@attrs
class TaskLog(Base):
    start_time = attrib(
        default=None,
        converter=timestampconv,
        validator=optional(instance_of(datetime))
    )
    end_time = attrib(
        default=None,
        converter=timestampconv,
        validator=optional(instance_of(datetime))
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
    system_logs = attrib(
        default=None, validator=optional(list_of(str))
    )


@attrs
class Task(Base):
    id = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    state = attrib(
        default=None,
        validator=optional(in_(
            ["UNKNOWN", "QUEUED", "INITIALIZING", "RUNNING", "COMPLETE",
             "CANCELED", "EXECUTOR_ERROR", "SYSTEM_ERROR"]
        ))
    )
    name = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    description = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    inputs = attrib(
        default=None, validator=optional(list_of(Input))
    )
    outputs = attrib(
        default=None, validator=optional(list_of(Output))
    )
    resources = attrib(
        default=None, validator=optional(instance_of(Resources))
    )
    executors = attrib(
        default=None, validator=optional(list_of(Executor))
    )
    volumes = attrib(
        default=None, validator=optional(list_of(str))
    )
    tags = attrib(
        default=None, validator=optional(instance_of(dict))
    )
    logs = attrib(
        default=None, validator=optional(list_of(TaskLog))
    )
    creation_time = attrib(
        default=None,
        converter=timestampconv,
        validator=optional(instance_of(datetime))
    )

    def is_valid(self):
        errs = []
        if self.executors is None or len(self.executors) == 0:
            errs.append("Must provide one or more Executors")
        else:
            for e in self.executors:
                if e.image is None:
                    errs.append("Executor image must be provided")
                if len(e.command) == 0:
                    errs.append("Executor command must be provided")
                if e.stdin is not None:
                    if not os.path.isabs(e.stdin):
                        errs.append("Executor stdin must be an absolute path")
                if e.stdout is not None:
                    if not os.path.isabs(e.stdout):
                        errs.append("Executor stdout must be an absolute path")
                if e.stderr is not None:
                    if not os.path.isabs(e.stderr):
                        errs.append("Executor stderr must be an absolute path")
                if e.env is not None:
                    for k, v in self.executors.env:
                        if not isinstance(k, str) and not isinstance(k, str):
                            errs.append(
                                "Executor env keys and values must be StrType"
                            )

        if self.inputs is not None:
            for i in self.inputs:
                if i.url is None and i.content is None:
                    errs.append("Input url must be provided")
                if i.url is not None and i.content is not None:
                    errs.append("Input url and content are mutually exclusive")
                if i.path is None:
                    errs.append("Input path must be provided")
                elif not os.path.isabs(i.path):
                    errs.append("Input path must be absolute")

        if self.outputs is not None:
            for o in self.outputs:
                if o.url is None:
                    errs.append("Output url must be provided")
                if o.path is None:
                    errs.append("Output path must be provided")
                elif not os.path.isabs(i.path):
                    errs.append("Output path must be absolute")

        if self.volumes is not None:
            if len(self.volumes) > 0:
                for v in self.volumes:
                    if not os.path.isabs(v):
                        errs.append("Volume paths must be absolute")

        if self.tags is not None:
            for k, v in self.tags:
                if not isinstance(k, str) and not isinstance(k, str):
                    errs.append(
                        "Tag keys and values must be StrType"
                    )

        if len(errs) > 0:
            return False, TypeError("\n".join(errs))

        return True, None


@attrs
class GetTaskRequest(Base):
    id = attrib(
        converter=strconv, validator=instance_of(str)
    )
    view = attrib(
        default=None, validator=optional(in_(["MINIMAL", "BASIC", "FULL"]))
    )


@attrs
class CreateTaskResponse(Base):
    id = attrib(
        converter=strconv, validator=instance_of(str)
    )


@attrs
class ServiceInfoRequest(Base):
    pass


@attrs
class ServiceInfo(Base):
    name = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    doc = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    storage = attrib(
        default=None, converter=strconv, validator=optional(list_of(str))
    )


@attrs
class CancelTaskRequest(Base):
    id = attrib(
        converter=strconv, validator=instance_of(str)
    )


@attrs
class CancelTaskResponse(Base):
    pass


@attrs
class ListTasksRequest(Base):
    project = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    name_prefix = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    page_size = attrib(
        default=None, validator=optional(instance_of(int))
    )
    page_token = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    view = attrib(
        default=None, validator=optional(in_(["MINIMAL", "BASIC", "FULL"]))
    )


@attrs
class ListTasksResponse(Base):
    tasks = attrib(
        default=None, validator=optional(list_of(Task))
    )
    next_page_token = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
