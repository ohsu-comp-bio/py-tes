import unittest
import tes


class TestTESClient(unittest.TestCase):
    def setUp(self):
        self.cli = tes.HTTPClient("http://localhost:8000", timeout=5)
        self.task = tes.Task(
            executors=[
                tes.Executor(
                    image="alpine",
                    command=["echo", "hello"]
                )
            ]
        )

    def test_task_creation(self):
        # Test service info retrieval
        service_info = self.cli.get_service_info()
        self.assertIsNotNone(service_info)

        # Test task creation
        task_id = self.cli.create_task(self.task)
        self.assertIsNotNone(task_id)

        # Wait for task to complete
        _ = self.cli.wait(task_id)

        # Test task info retrieval
        task_info = self.cli.get_task(task_id, view="BASIC")
        self.assertIsNotNone(task_info)


if __name__ == '__main__':
    unittest.main()
