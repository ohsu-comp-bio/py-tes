from __future__ import absolute_import, print_function, unicode_literals

import dateutil.parser
import json
import unittest

from tes.utils import camel_to_snake, unmarshal, UnmarshalError
from tes.models import Input, Task, CreateTaskResponse


class TestUtils(unittest.TestCase):

    def test_camel_to_snake(self):
        case1 = "FooBar"
        case2 = "fooBar"
        case3 = "foo_bar"
        self.assertEqual(camel_to_snake(case1), "foo_bar")
        self.assertEqual(camel_to_snake(case2), "foo_bar")
        self.assertEqual(camel_to_snake(case3), "foo_bar")

    def test_unmarshal(self):
        test_invalid_dict = {"adfasd": "bar"}
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
        o2 = unmarshal(test_simple_str, Input)
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
            "creation_time": "2017-10-09T17:00:00.0Z"
        }

        test_complex_str = json.dumps(test_complex_dict)
        o1 = unmarshal(test_complex_dict, Task)
        o2 = unmarshal(test_complex_str, Task)
        self.assertTrue(isinstance(o1, Task))
        self.assertTrue(isinstance(o2, Task))
        self.assertEqual(o1, o2)
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
