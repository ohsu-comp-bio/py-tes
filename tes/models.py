from __future__ import absolute_import, print_function, unicode_literals

import dateutil.parser
import json
import os

from attr import asdict, attrs, attrib
from attr.validators import instance_of, optional, in_
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Type, Union


@attrs(repr=False)
class _ListOfValidator(object):
    type: Type = attrib()

    def __call__(self, inst, attr, value) -> None:
        if not all([isinstance(n, self.type) for n in value]):
            raise TypeError(
                f"'{attr.name}' must be a list of {self.type!r} (got "
                f"{value!r}", attr
            )

    def __repr__(self) -> str:
        return f"<instance_of validator for type {self.type!r}>"


def list_of(_type: Any) -> _ListOfValidator:
    return _ListOfValidator(_type)


def _drop_none(obj: Any) -> Any:
    if isinstance(obj, (list, tuple, set)):
        return type(obj)(_drop_none(x) for x in obj if x is not None)
    elif isinstance(obj, dict):
        return type(obj)(
            (_drop_none(k), _drop_none(v))
            for k, v in obj.items() if k is not None and v is not None
        )
    else:
        return obj


def strconv(value: Any) -> Any:
    if isinstance(value, (tuple, list)):
        if all([isinstance(n, str) for n in value]):
            return [str(n) for n in value]
        else:
            return value
    elif isinstance(value, str):
        return str(value)
    else:
        return value


# since an int64 value is encoded as a string in json we need to handle
# conversion
def int64conv(value: Optional[str]) -> Optional[int]:
    if value is None:
        return value
    return int(value)


def timestampconv(value: Optional[str]) -> Optional[datetime]:
    if value is None:
        return value
    return dateutil.parser.parse(value)


def datetime_json_handler(x: Any) -> str:
    if isinstance(x, datetime):
        return x.isoformat()
    raise TypeError("Unknown type")


@attrs
class Base(object):

    def as_dict(self, drop_empty: bool = True) -> Dict[str, Any]:
        obj = asdict(self)
        if drop_empty:
            return _drop_none(obj)
        return obj

    def as_json(self, drop_empty: bool = True, **kwargs) -> str:
        return json.dumps(
            self.as_dict(drop_empty),
            default=datetime_json_handler,
            **kwargs
        )


@attrs
class Input(Base):
    url: Optional[str] = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    path: Optional[str] = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    type: str = attrib(
        default="FILE", validator=in_(["FILE", "DIRECTORY"])
    )
    name: Optional[str] = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    description: Optional[str] = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    content: Optional[str] = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )


@attrs
class Output(Base):
    url: Optional[str] = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    path: Optional[str] = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    type: str = attrib(
        default="FILE", validator=in_(["FILE", "DIRECTORY"])
    )
    name: Optional[str] = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    description: Optional[str] = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )


@attrs
class Resources(Base):
    cpu_cores: Optional[int] = attrib(
        default=None, validator=optional(instance_of(int))
    )
    ram_gb: Optional[Union[float, int]] = attrib(
        default=None, validator=optional(instance_of((float, int)))
    )
    disk_gb: Optional[Union[float, int]] = attrib(
        default=None, validator=optional(instance_of((float, int)))
    )
    preemptible: Optional[bool] = attrib(
        default=None, validator=optional(instance_of(bool))
    )
    zones: Optional[List[str]] = attrib(
        default=None, converter=strconv, validator=optional(list_of(str))
    )


@attrs
class Executor(Base):
    image: str = attrib(
        converter=strconv, validator=instance_of(str)
    )
    command: List[str] = attrib(
        converter=strconv, validator=list_of(str)
    )
    workdir: str = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    stdin: str = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    stdout: str = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    stderr: str = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    env: Optional[Dict] = attrib(
        default=None, validator=optional(instance_of(dict))
    )


@attrs
class ExecutorLog(Base):
    start_time: datetime = attrib(
        default=None,
        converter=timestampconv,
        validator=optional(instance_of(datetime))
    )
    end_time: datetime = attrib(
        default=None,
        converter=timestampconv,
        validator=optional(instance_of(datetime))
    )
    stdout: Optional[str] = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    stderr: Optional[str] = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    exit_code: Optional[int] = attrib(
        default=None, validator=optional(instance_of(int))
    )


@attrs
class OutputFileLog(Base):
    url: Optional[str] = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    path: Optional[str] = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    size_bytes: Optional[int] = attrib(
        default=None, converter=int64conv, validator=optional(instance_of(int))
    )


@attrs
class TaskLog(Base):
    start_time: datetime = attrib(
        default=None,
        converter=timestampconv,
        validator=optional(instance_of(datetime))
    )
    end_time: datetime = attrib(
        default=None,
        converter=timestampconv,
        validator=optional(instance_of(datetime))
    )
    metadata: Optional[Dict] = attrib(
        default=None, validator=optional(instance_of(dict))
    )
    logs: Optional[List[ExecutorLog]] = attrib(
        default=None, validator=optional(list_of(ExecutorLog))
    )
    outputs: Optional[List[OutputFileLog]] = attrib(
        default=None, validator=optional(list_of(OutputFileLog))
    )
    system_logs: Optional[List[str]] = attrib(
        default=None, validator=optional(list_of(str))
    )


@attrs
class Task(Base):
    id: Optional[str] = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    state: Optional[str] = attrib(
        default=None,
        validator=optional(in_(
            ["UNKNOWN", "QUEUED", "INITIALIZING", "RUNNING", "COMPLETE",
             "CANCELED", "EXECUTOR_ERROR", "SYSTEM_ERROR"]
        ))
    )
    name: Optional[str] = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    description: Optional[str] = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    inputs: Optional[List[Input]] = attrib(
        default=None, validator=optional(list_of(Input))
    )
    outputs: Optional[List[Output]] = attrib(
        default=None, validator=optional(list_of(Output))
    )
    resources: Optional[Resources] = attrib(
        default=None, validator=optional(instance_of(Resources))
    )
    executors: Optional[List[Executor]] = attrib(
        default=None, validator=optional(list_of(Executor))
    )
    volumes: Optional[List[str]] = attrib(
        default=None, validator=optional(list_of(str))
    )
    tags: Optional[Dict] = attrib(
        default=None, validator=optional(instance_of(dict))
    )
    logs: Optional[List[TaskLog]] = attrib(
        default=None, validator=optional(list_of(TaskLog))
    )
    creation_time: datetime = attrib(
        default=None,
        converter=timestampconv,
        validator=optional(instance_of(datetime))
    )

    def is_valid(self) -> Tuple[bool, Union[None, TypeError]]:
        errs = []
        if self.executors is None or len(self.executors) == 0:
            errs.append("Must provide one or more Executors")
        else:
            for e in self.executors:
                if e.image is None:
                    errs.append("Executor image must be provided")
                if e.command is None or len(e.command) == 0:
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
                    for k, v in e.env.items():
                        if not isinstance(k, str) and not isinstance(v, str):
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
                elif not os.path.isabs(o.path):
                    errs.append("Output path must be absolute")

        if self.volumes is not None:
            if len(self.volumes) > 0:
                for v in self.volumes:
                    if not os.path.isabs(v):
                        errs.append("Volume paths must be absolute")

        if self.tags is not None:
            for k, v in self.tags.items():
                if not isinstance(k, str) and not isinstance(k, str):
                    errs.append(
                        "Tag keys and values must be StrType"
                    )

        if len(errs) > 0:
            return False, TypeError("\n".join(errs))

        return True, None


@attrs
class GetTaskRequest(Base):
    id: str = attrib(
        converter=strconv, validator=instance_of(str)
    )
    view: Optional[str] = attrib(
        default=None, validator=optional(in_(["MINIMAL", "BASIC", "FULL"]))
    )


@attrs
class CreateTaskResponse(Base):
    id: str = attrib(
        converter=strconv, validator=instance_of(str)
    )


@attrs
class ServiceInfoRequest(Base):
    pass


@attrs
class ServiceInfo(Base):
    name: Optional[str] = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    doc: Optional[str] = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    storage: Optional[List[str]] = attrib(
        default=None, converter=strconv, validator=optional(list_of(str))
    )


@attrs
class CancelTaskRequest(Base):
    id: str = attrib(
        converter=strconv, validator=instance_of(str)
    )


@attrs
class CancelTaskResponse(Base):
    pass


@attrs
class ListTasksRequest(Base):
    project: Optional[str] = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    name_prefix: Optional[str] = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    page_size: Optional[int] = attrib(
        default=None, validator=optional(instance_of(int))
    )
    page_token: Optional[str] = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
    view: Optional[str] = attrib(
        default=None, validator=optional(in_(["MINIMAL", "BASIC", "FULL"]))
    )


@attrs
class ListTasksResponse(Base):
    tasks: Optional[List[Task]] = attrib(
        default=None, validator=optional(list_of(Task))
    )
    next_page_token: Optional[str] = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str))
    )
