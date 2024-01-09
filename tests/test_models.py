import json
import unittest

from copy import deepcopy

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


task_valid = Task(
    executors=[
        Executor(
            image="alpine",
            command=["echo", "hello"]
        )
    ]
)


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
            env={"VAR": "value"}
        ),
        Executor(
            image="alpine",
            command=["echo", "worls"]
        )
    ],
    inputs=[
        Input(
            url="s3:/some/path",
            path="/abs/path"
        ),
        Input(
            content="foo",
            path="/abs/path"
        )
    ],
    outputs=[
        Output(
            url="s3:/some/path",
            path="/abs/path"
        )
    ],
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
                    stderr="world"
                )
            ],
            outputs=[
                OutputFileLog(
                    url="s3:/some/path",
                    path="/abs/path",
                    size_bytes=int64conv(123)  # type: ignore
                )
            ],
            system_logs=[
                "some system log message",
                "some other system log message"
            ]
        )
    ],
    creation_time=datetm  # type: ignore
)

task_invalid = Task(
    executors=[
        Executor(  # type: ignore
            image="alpine",
            command=["echo", "hello"],
            stdin="relative/path",
            stdout="relative/path",
            stderr="relative/path",
            env={1: 2}
        )
    ],
    inputs=[
        Input(
            url="s3:/some/path",
            content="foo"
        ),
        Input(
            path="relative/path"
        )
    ],
    outputs=[
        Output(),
        Output(
            url="s3:/some/path",
            path="relative/path"
        )
    ],
    volumes=['/abs/path', 'relative/path'],
    tags={1: 2}
)

expected = {
    "executors": [
        {
            "image": "alpine",
            "command": ["echo", "hello"]
        }
    ]
}


class TestModels(unittest.TestCase):

    def test_list_of(self):
        validator = list_of(str)
        self.assertEqual(list_of(str), validator)
        self.assertEqual(
            repr(validator),
            "<instance_of validator for type <class 'str'>>"
        )
        with self.assertRaises(TypeError):
            Input(
                url="s3:/some/path",
                path="/opt/foo",
                content=123  # type: ignore
            )
        with self.assertRaises(TypeError):
            Task(
                inputs=[
                    Input(
                        url="s3:/some/path", path="/opt/foo"
                    ),
                    "foo"  # type: ignore
                ]
            )

    def test_drop_none(self):
        self.assertEqual(_drop_none({}), {})
        self.assertEqual(_drop_none({"foo": None}), {})
        self.assertEqual(_drop_none({"foo": 1}), {"foo": 1})
        self.assertEqual(_drop_none({"foo": None, "bar": 1}), {"bar": 1})
        self.assertEqual(_drop_none({"foo": [1, None, 2]}), {"foo": [1, 2]})
        self.assertEqual(_drop_none({"foo": {"bar": None}}), {"foo": {}})
        self.assertEqual(
            _drop_none({"foo": {"bar": None}, "baz": 1}),
            {"foo": {}, "baz": 1}
        )

    def test_strconv(self):
        self.assertTrue(strconv("foo"), u"foo")
        self.assertTrue(strconv(["foo", "bar"]), [u"foo", u"bar"])
        self.assertTrue(strconv(("foo", "bar")), (u"foo", u"bar"))
        self.assertTrue(strconv(1), 1)
        self.assertTrue(strconv([1]), [1])

    def test_int64conv(self):
        self.assertEqual(int64conv("1"), 1)
        self.assertEqual(int64conv("-1"), -1)
        self.assertIsNone(int64conv(None))

    def test_timestampconv(self):
        tm = timestampconv("2018-02-01T00:00:00Z")
        self.assertIsNotNone(tm)
        assert tm is not None
        self.assertAlmostEqual(tm.year, 2018)
        self.assertAlmostEqual(tm.month, 2)
        self.assertAlmostEqual(tm.day, 1)
        self.assertAlmostEqual(tm.hour, 0)
        self.assertAlmostEqual(tm.timestamp(), 1517443200.0)
        self.assertIsNone(timestampconv(None))

    def test_datetime_json_handler(self):
        tm = timestampconv("2018-02-01T00:00:00Z")
        tm_iso = '2018-02-01T00:00:00+00:00'
        assert tm is not None
        self.assertEqual(datetime_json_handler(tm), tm_iso)
        with self.assertRaises(TypeError):
            datetime_json_handler(None)
        with self.assertRaises(TypeError):
            datetime_json_handler("abc")
        with self.assertRaises(TypeError):
            datetime_json_handler(2001)
        with self.assertRaises(TypeError):
            datetime_json_handler(tm_iso)

    def test_as_dict(self):
        task = deepcopy(task_valid)
        self.assertEqual(task.as_dict(), expected)
        with self.assertRaises(KeyError):
            task.as_dict()['inputs']
        self.assertIsNone(task.as_dict(drop_empty=False)['inputs'])

    def test_as_json(self):
        task = deepcopy(task_valid)
        self.assertEqual(task.as_json(), json.dumps(expected))

    def test_is_valid(self):
        task = deepcopy(task_valid)
        self.assertTrue(task.is_valid()[0])

        task = deepcopy(task_valid_full)
        self.assertTrue(task.is_valid()[0])

        task = deepcopy(task_invalid)
        task.executors[0].image = None  # type: ignore
        task.executors[0].command = None  # type: ignore
        self.assertFalse(task.is_valid()[0])

        task = deepcopy(task_invalid)
        task.executors = None
        self.assertFalse(task.is_valid()[0])
