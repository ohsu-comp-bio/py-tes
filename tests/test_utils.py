import json
import unittest

from tes.utils import camel_to_snake, json2obj
from tes.models import TaskParameter, Task


class TestUtils(unittest.TestCase):

    def test_camel_to_snake(self):
        case1 = "FooBar"
        case2 = "fooBar"
        case3 = "foo_bar"
        self.assertEqual(camel_to_snake(case1), "foo_bar")
        self.assertEqual(camel_to_snake(case2), "foo_bar")
        self.assertEqual(camel_to_snake(case3), "foo_bar")

    def test_json2obj(self):
        test_simple_dict = {
            "url": "file://test_file",
            "path": "/mnt/test_file",
            "type": "FILE"
        }
        test_simple_str = json.dumps(test_simple_dict)
        o1 = json2obj(test_simple_dict, TaskParameter)
        o2 = json2obj(test_simple_str, TaskParameter)
        self.assertTrue(isinstance(o1, TaskParameter))
        self.assertTrue(isinstance(o2, TaskParameter))
        self.assertEqual(o1, o2)
        self.assertEqual(o1.as_dict(), test_simple_dict)
        self.assertEqual(o1.as_json(), test_simple_str)

        test_complex_dict = {
            "name": "test",
            "inputs": [
                {
                    "url": "file://test_file",
                    "path": "/mnt/test_file",
                    "type": "FILE"
                }
            ],
            "executors": [
                {
                    "image_name": "alpine",
                    "cmd": ["echo", "hello"]
                }
            ]
        }
        test_complex_str = json.dumps(test_complex_dict)
        o1 = json2obj(test_complex_dict, Task)
        o2 = json2obj(test_complex_str, Task)
        self.assertTrue(isinstance(o1, Task))
        self.assertTrue(isinstance(o2, Task))
        self.assertEqual(o1, o2)
        self.assertEqual(o1.as_dict(), test_complex_dict)
        self.assertEqual(o1.as_json(), test_complex_str)
