import dateutil.parser
import json
import unittest

from tes.utils import camel_to_snake, unmarshal, UnmarshalError
from tes.models import TaskParameter, Task, CreateTaskResponse


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
        o1 = unmarshal(test_simple_dict, TaskParameter)
        o2 = unmarshal(test_simple_str, TaskParameter)
        self.assertTrue(isinstance(o1, TaskParameter))
        self.assertTrue(isinstance(o2, TaskParameter))
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
                    "image_name": "alpine",
                    "cmd": ["echo", "hello"],
                    "ports": [{"host": 0, "container": 8000}]
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
                            "host_ip": "127.0.0.1",
                            "ports": [{"host": 8888, "container": 8000}]
                        }
                    ],
                    "outputs": [
                        {
                            "url": "file:///storage/outputs/test_outputfile",
                            "path": "/mnt/test_outputfile",
                            "size_bytes": "3333"
                        }
                    ]
                }
            ]
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

        self.assertEqual(o1.as_dict(), expected)
