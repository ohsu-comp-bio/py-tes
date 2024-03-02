from __future__ import absolute_import, print_function, unicode_literals

import dateutil.parser
import json
import unittest

from tes.utils import camel_to_snake, unmarshal, UnmarshalError
from tes.models import (
    CancelTaskRequest,
    CancelTaskResponse,
    CreateTaskResponse,
    Executor,
    ExecutorLog,
    GetTaskRequest,
    Input,
    ListTasksRequest,
    ListTasksResponse,
    Output,
    OutputFileLog,
    Resources,
    ServiceInfo,
    Task,
    TaskLog,
)


class TestUtils(unittest.TestCase):

    def test_camel_to_snake(self):
        case1 = "FooBar"
        case2 = "fooBar"
        case3 = "foo_bar"
        self.assertEqual(camel_to_snake(case1), "foo_bar")
        self.assertEqual(camel_to_snake(case2), "foo_bar")
        self.assertEqual(camel_to_snake(case3), "foo_bar")

    def test_unmarshal(self):

        # test unmarshalling with no or minimal contents
        try:
            unmarshal(
                CancelTaskRequest(id="foo").as_json(),
                CancelTaskRequest
            )
        except Exception:
            self.fail("Raised ExceptionType unexpectedly!")

        try:
            unmarshal(CancelTaskResponse().as_json(), CancelTaskResponse)
        except Exception:
            self.fail("Raised ExceptionType unexpectedly!")

        try:
            unmarshal(
                CreateTaskResponse(id="foo").as_json(),
                CreateTaskResponse
            )
        except Exception:
            self.fail("Raised ExceptionType unexpectedly!")

        try:
            unmarshal(Executor(
                image="alpine", command=["echo", "hello"]).as_json(),
                Executor
            )
        except Exception:
            self.fail("Raised ExceptionType unexpectedly!")

        try:
            unmarshal(ExecutorLog().as_json(), ExecutorLog)
        except Exception:
            self.fail("Raised ExceptionType unexpectedly!")

        try:
            unmarshal(
                GetTaskRequest(id="foo", view="BASIC").as_json(),
                GetTaskRequest
            )
        except Exception:
            self.fail("Raised ExceptionType unexpectedly!")

        try:
            unmarshal(Input().as_json(), Input)
        except Exception:
            self.fail("Raised ExceptionType unexpectedly!")

        try:
            unmarshal(ListTasksRequest().as_json(), ListTasksRequest)
        except Exception:
            self.fail("Raised ExceptionType unexpectedly!")

        try:
            unmarshal(ListTasksResponse().as_json(), ListTasksResponse)
        except Exception:
            self.fail("Raised ExceptionType unexpectedly!")

        try:
            unmarshal(Output().as_json(), Output)
        except Exception:
            self.fail("Raised ExceptionType unexpectedly!")

        try:
            unmarshal(OutputFileLog().as_json(), OutputFileLog)
        except Exception:
            self.fail("Raised ExceptionType unexpectedly!")

        try:
            unmarshal(Resources().as_json(), Resources)
        except Exception:
            self.fail("Raised ExceptionType unexpectedly!")

        try:
            unmarshal(ServiceInfo().as_json(), ServiceInfo)
        except Exception:
            self.fail("Raised ExceptionType unexpectedly!")

        try:
            unmarshal(Task().as_json(), Task)
        except Exception:
            self.fail("Raised ExceptionType unexpectedly!")

        try:
            unmarshal(TaskLog().as_json(), TaskLog)
        except Exception:
            self.fail("Raised ExceptionType unexpectedly!")

        # test special cases
        self.assertIsNone(unmarshal(None, Input))
        with self.assertRaises(TypeError):
            unmarshal([], Input)
        with self.assertRaises(TypeError):
            unmarshal(1, Input)
        with self.assertRaises(TypeError):
            unmarshal(1.3, Input)
        with self.assertRaises(TypeError):
            unmarshal(True, Input)
        with self.assertRaises(TypeError):
            unmarshal('foo', Input)

        # test with some interesting contents
        test_invalid_dict = {"foo": "bar"}
        test_invalid_str = json.dumps(test_invalid_dict)
        with self.assertRaises(UnmarshalError):
            unmarshal(test_invalid_dict, CreateTaskResponse)
        with self.assertRaises(UnmarshalError):
            unmarshal(test_invalid_str, CreateTaskResponse)

        test_simple_dict = {
            "url": "file://test_file",
            "path": "/mnt/test_file",
            "type": "FILE"
        }
        test_simple_str = json.dumps(test_simple_dict)
        o1 = unmarshal(test_simple_dict, Input)
        o2 = unmarshal(test_simple_str, Input, convert_camel_case=False)
        self.assertTrue(isinstance(o1, Input))
        self.assertTrue(isinstance(o2, Input))
        self.assertEqual(o1, o2)
        self.assertEqual(o1.as_dict(), test_simple_dict)
        self.assertEqual(o1.as_json(), test_simple_str)

        test_complex_dict = {
            "name": "test",
            "inputs": [
                {
                    "url": "file:///storage/inputs/test_file",
                    "path": "/mnt/test_file",
                    "type": "FILE"
                }
            ],
            "outputs": [
                {
                    "url": "file:///storage/outputs/test_outputfile",
                    "path": "/mnt/test_outputfile",
                    "type": "FILE"
                }
            ],
            "executors": [
                {
                    "image": "alpine",
                    "command": ["echo", "hello"],
                    "env": {"HOME": "/home/"}
                }
            ],
            "logs": [
                {
                    "start_time": "2017-10-09T17:05:00.0Z",
                    "end_time": "2017-10-09T17:40:30.0Z",
                    "metadata": {"testmeta": "testvalue"},
                    "logs": [
                        {
                            "start_time": "2017-10-09T17:06:30.0Z",
                            "end_time": "2017-10-09T17:39:50.0Z",
                            "exit_code": 0,
                            "stdout": "hello",
                            "stderr": "",
                        }
                    ],
                    "outputs": [
                        {
                            "url": "file:///storage/outputs/test_outputfile",
                            "path": "/mnt/test_outputfile",
                            "size_bytes": "3333"
                        }
                    ],
                    "system_logs": [
                        "level='info' msg='Download started' \
                        timestamp='2018-05-04T09:12:42.391262682-07:00' \
                        task_attempt='0' executor_index='0' \
                        url='swift://biostream/protograph'"
                    ]
                }
            ],
            "resources": {
                "cpu_cores": 1,
                "ram_gb": 2,
                "disk_gb": 3,
                "preemptible": True,
                "zones": ["us-east-1", "us-west-1"]
            },
            "creation_time": "2017-10-09T17:00:00.0Z"
        }

        test_complex_str = json.dumps(test_complex_dict)
        o1 = unmarshal(test_complex_dict, Task)
        o2 = unmarshal(test_complex_str, Task)
        self.assertTrue(isinstance(o1, Task))
        self.assertTrue(isinstance(o2, Task))
        self.assertAlmostEqual(o1, o2)
        expected = test_complex_dict.copy()

        # handle expected conversions
        expected["logs"][0]["outputs"][0]["size_bytes"] = int(
            expected["logs"][0]["outputs"][0]["size_bytes"]
        )
        expected["logs"][0]["start_time"] = dateutil.parser.parse(
            expected["logs"][0]["start_time"]
        )
        expected["logs"][0]["end_time"] = dateutil.parser.parse(
            expected["logs"][0]["end_time"]
        )
        expected["logs"][0]["logs"][0]["start_time"] = dateutil.parser.parse(
            expected["logs"][0]["logs"][0]["start_time"]
        )
        expected["logs"][0]["logs"][0]["end_time"] = dateutil.parser.parse(
            expected["logs"][0]["logs"][0]["end_time"]
        )
        expected["creation_time"] = dateutil.parser.parse(
            expected["creation_time"]
        )
        self.assertEqual(o1.as_dict(), expected)

    def test_unmarshal_types(self):

        empty_log_dict = {
            'id': 'c55qjplpsjir0oo1kdj0',
            'state': 'QUEUED',
            'name': 'toil-bbc72af7-e11a-4831-9392-669ea6c309a1-0',
            'executors': [{
                'image':
                    'testImage',
                'command': [
                    '_toil_kubernetes_executor',
                    'gAWVGwAAAAAAAAB9lIwHY29tbWFuZJSMCnNsZWVwIDEwMDCUcy4='
                ]
            }],
            'logs': [{}],
            'creation_time': "2017-10-09T17:00:00"
        }

        expected = empty_log_dict.copy()
        expected["creation_time"] = dateutil.parser.parse(
            expected["creation_time"]
        )

        empty_log_str = json.dumps(empty_log_dict)
        o1 = unmarshal(empty_log_dict, Task)

        self.assertEqual(o1.as_dict(), expected)
        self.assertEqual(o1.as_json(), empty_log_str)
