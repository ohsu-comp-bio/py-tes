import json
from copy import deepcopy
from datetime import datetime

import pytest

from tes.models import (
    Executor,
    ExecutorLog,
    Input,
    Output,
    OutputFileLog,
    Resources,
    Task,
    TaskLog,
    datetime_json_handler,
    int64conv,
    list_of,
    strconv,
    timestampconv,
    _drop_none,
)


task_valid = Task(executors=[Executor(image="alpine", command=["echo", "hello"])])


datetm = "2018-01-01T00:00:00Z"
task_valid_full = Task(
    id="foo",
    state="COMPLETE",
    name="some_task",
    description="some description",
    resources=Resources(
        cpu_cores=1,
        ram_gb=2,
        disk_gb=3,
        preemptible=True,
        zones=["us-east-1", "us-west-1"],
    ),
    executors=[
        Executor(
            image="alpine",
            command=["echo", "hello"],
            workdir="/abs/path",
            stdin="/abs/path",
            stdout="/abs/path",
            stderr="/abs/path",
            env={"VAR": "value"},
        ),
        Executor(image="alpine", command=["echo", "worls"]),
    ],
    inputs=[
        Input(url="s3:/some/path", path="/abs/path"),
        Input(content="foo", path="/abs/path"),
    ],
    outputs=[Output(url="s3:/some/path", path="/abs/path")],
    volumes=[],
    tags={"key": "value", "key2": "value2"},
    logs=[
        TaskLog(
            start_time=datetm,  # type: ignore
            end_time=datetm,  # type: ignore
            metadata={"key": "value", "key2": "value2"},
            logs=[
                ExecutorLog(
                    start_time=datetm,  # type: ignore
                    end_time=datetm,  # type: ignore
                    exit_code=0,
                    stdout="hello",
                    stderr="world",
                )
            ],
            outputs=[
                OutputFileLog(
                    url="s3:/some/path",
                    path="/abs/path",
                    size_bytes=int64conv(123),  # type: ignore
                )
            ],
            system_logs=["some system log message", "some other system log message"],
        )
    ],
    creation_time=datetm,  # type: ignore
)

task_invalid = Task(
    executors=[
        Executor(  # type: ignore
            image="alpine",
            command=["echo", "hello"],
            stdin="relative/path",
            stdout="relative/path",
            stderr="relative/path",
            env={1: 2},
        )
    ],
    inputs=[Input(url="s3:/some/path", content="foo"), Input(path="relative/path")],
    outputs=[Output(), Output(url="s3:/some/path", path="relative/path")],
    volumes=["/abs/path", "relative/path"],
    tags={1: 2},
)

expected = {"executors": [{"image": "alpine", "command": ["echo", "hello"]}]}


def test_list_of():
    validator = list_of(str)
    assert list_of(str) == validator
    assert repr(validator) == "<instance_of validator for type <class 'str'>>"
    with pytest.raises(TypeError):
        Input(url="s3:/some/path", path="/opt/foo", content=123)  # type: ignore
    with pytest.raises(TypeError):
        Task(
            inputs=[Input(url="s3:/some/path", path="/opt/foo"), "foo"]  # type: ignore
        )


def test_drop_none():
    assert _drop_none({}) == {}
    assert _drop_none({"foo": None}) == {}
    assert _drop_none({"foo": 1}) == {"foo": 1}
    assert _drop_none({"foo": None, "bar": 1}) == {"bar": 1}
    assert _drop_none({"foo": [1, None, 2]}) == {"foo": [1, 2]}
    assert _drop_none({"foo": {"bar": None}}) == {"foo": {}}
    assert _drop_none({"foo": {"bar": None}, "baz": 1}) == {"foo": {}, "baz": 1}


def test_strconv():
    assert strconv("foo") == "foo"
    assert strconv(["foo", "bar"]) == ["foo", "bar"]
    assert strconv(("foo", "bar")) == ("foo", "bar")
    assert strconv(1) == 1
    assert strconv([1]) == [1]


def test_int64conv():
    assert int64conv("1") == 1
    assert int64conv("-1") == -1
    assert int64conv(None) is None


def test_timestampconv():
    tm = timestampconv("2018-02-01T00:00:00Z")
    assert tm is not None
    assert tm.year == 2018
    assert tm.month == 2
    assert tm.day == 1
    assert tm.hour == 0
    assert tm.timestamp() == 1517443200.0
    assert timestampconv(None) is None


def test_datetime_json_handler():
    tm = timestampconv("2018-02-01T00:00:00Z")
    tm_iso = "2018-02-01T00:00:00+00:00"
    assert tm is not None
    assert datetime_json_handler(tm) == tm_iso
    with pytest.raises(TypeError):
        datetime_json_handler(None)
    with pytest.raises(TypeError):
        datetime_json_handler("abc")
    with pytest.raises(TypeError):
        datetime_json_handler(2001)
    with pytest.raises(TypeError):
        datetime_json_handler(tm_iso)


def test_as_dict():
    task = deepcopy(task_valid)
    assert task.as_dict() == expected
    with pytest.raises(KeyError):
        task.as_dict()["inputs"]
    assert task.as_dict(drop_empty=False)["inputs"] is None


def test_as_json():
    task = deepcopy(task_valid)
    assert task.as_json() == json.dumps(expected)


def test_is_valid():
    task = deepcopy(task_valid)
    assert task.is_valid()[0]

    task = deepcopy(task_valid_full)
    assert task.is_valid()[0]

    task = deepcopy(task_invalid)
    task.executors[0].image = None  # type: ignore
    task.executors[0].command = None  # type: ignore
    assert not task.is_valid()[0]

    task = deepcopy(task_invalid)
    task.executors = None
    assert not task.is_valid()[0]


def test_task_creation():
    task = Task(
        id="test_id",
        state="RUNNING",
        name="test_task",
        description="test description",
        executors=[Executor(image="python:3.8", command=["python", "--version"])],
        creation_time=datetime.now(),
    )
    assert task.id == "test_id"
    assert task.state == "RUNNING"
    assert task.name == "test_task"
    assert task.description == "test description"
    assert len(task.executors) == 1
    assert task.executors[0].image == "python:3.8"
    assert task.executors[0].command == ["python", "--version"]
    assert task.creation_time is not None


def test_task_invalid_state():
    with pytest.raises(ValueError):
        Task(
            id="test_id",
            state="INVALID_STATE",  # type: ignore
            name="test_task",
            description="test description",
            executors=[Executor(image="python:3.8", command=["python", "--version"])],
            creation_time=datetime.now(),
        )


def test_executor_missing_image():
    with pytest.raises(TypeError):
        Executor(command=["python", "--version"])


def test_executor_missing_command():
    with pytest.raises(TypeError):
        Executor(image="python:3.8")
