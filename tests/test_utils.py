import json
import unittest

from tes.utils import camel_to_snake, unmarshal
from tes.models import TaskParameter, Task


class TestUtils(unittest.TestCase):

    def test_camel_to_snake(self):
        case1 = "FooBar"
        case2 = "fooBar"
        case3 = "foo_bar"
        self.assertEqual(camel_to_snake(case1), "foo_bar")
        self.assertEqual(camel_to_snake(case2), "foo_bar")
        self.assertEqual(camel_to_snake(case3), "foo_bar")

    def test_unmarshal(self):
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
                    "start_time": "1",
                    "end_time": "5",
                    "metadata": {"testmeta": "testvalue"},
                    "logs": [
                        {
                            "start_time": "1",
                            "end_time": "5",
                            "exit_code": 0,
                            "host_ip": "127.0.0.1",
                            "ports": [{"host": 8888, "container": 8000}]
                        }
                    ],
                    "outputs": [
                        {
                            "url": "file:///storage/outputs/test_outputfile",
                            "path": "/mnt/test_outputfile",
                            "size_bytes": 33
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
        self.assertEqual(o1.as_dict(), test_complex_dict)
