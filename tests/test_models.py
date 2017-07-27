import json
import unittest

from tes.models import Task, Executor, TaskParameter


class TestModels(unittest.TestCase):
    task = Task(
        executors=[
            Executor(
                image_name="alpine",
                cmd=["echo", "hello"]
            )
        ]
    )

    expected = {
        "executors": [
            {
                "image_name": "alpine",
                "cmd": ["echo", "hello"]
            }
        ]
    }

    def test_as_dict(self):
        self.assertEqual(self.task.as_dict(), self.expected)

    def test_as_json(self):
        self.assertEqual(self.task.as_json(), json.dumps(self.expected))

    def test_is_valid(self):
        self.assertTrue(self.task.is_valid()[0])

        task2 = self.task
        task2.inputs = [TaskParameter(path="foo")]
        self.assertFalse(task2.is_valid()[0])

        task3 = self.task
        task3.outputs = [
            TaskParameter(
                url="s3:/some/path", path="foo", contents="content"
            )
        ]
        self.assertFalse(task3.is_valid()[0])
