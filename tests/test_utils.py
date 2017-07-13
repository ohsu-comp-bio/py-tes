from __future__ import print_function

import json
import unittest

from tes.utils import camel_to_snake, json2obj
from tes.models import TaskParameter


class TestUtils(unittest.TestCase):

    def test_camel_to_snake(self):
        case1 = "FooBar"
        case2 = "fooBar"
        case3 = "foo_bar"
        assert camel_to_snake(case1) == "foo_bar"
        assert camel_to_snake(case2) == "foo_bar"
        assert camel_to_snake(case3) == "foo_bar"

    def test_json2obj(self):
        test_dict = {
            "url": "file://test_file",
            "path": "/mnt/test_file",
            "type": "FILE"
        }
        test_str = json.dumps(test_dict)
        o1 = json2obj(test_dict, TaskParameter)
        o2 = json2obj(test_str, TaskParameter)
        assert isinstance(o1, TaskParameter)
        assert isinstance(o2, TaskParameter)
        assert o1 == o2
