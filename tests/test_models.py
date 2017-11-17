import json
import unittest

from tes.models import Task, Executor, Input, Output, strconv


class TestModels(unittest.TestCase):
    task = Task(
        executors=[
            Executor(
                image="alpine",
                command=["echo", "hello"]
            )
        ]
    )

    expected = {
        "executors": [
            {
                "image": "alpine",
                "command": ["echo", "hello"]
            }
        ]
    }

    def test_strconv(self):
        self.assertTrue(strconv("foo"), u"foo")
        self.assertTrue(strconv(["foo", "bar"]), [u"foo", u"bar"])
        self.assertTrue(strconv(("foo", "bar")), (u"foo", u"bar"))
        self.assertTrue(strconv(1), 1)

        with self.assertRaises(TypeError):
            Input(
                url="s3:/some/path", path="/opt/foo", content=123
            )

    def test_list_of(self):
        with self.assertRaises(TypeError):
            Task(
                inputs=[
                    Input(
                        url="s3:/some/path", path="/opt/foo"
                    ),
                    "foo"
                ]
            )

    def test_as_dict(self):
        self.assertEqual(self.task.as_dict(), self.expected)

    def test_as_json(self):
        self.assertEqual(self.task.as_json(), json.dumps(self.expected))

    def test_is_valid(self):
        self.assertTrue(self.task.is_valid()[0])

        task2 = self.task
        task2.inputs = [Input(path="/opt/foo")]
        self.assertFalse(task2.is_valid()[0])

        task3 = self.task
        task3.outputs = [
            Output(
                url="s3:/some/path", path="foo"
            )
        ]
        self.assertFalse(task3.is_valid()[0])
