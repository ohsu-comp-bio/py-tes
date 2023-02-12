import requests
import requests_mock
import unittest
import uuid

from tes.client import HTTPClient
from tes.models import Task, Executor
from tes.utils import TimeoutError


class TestHTTPClient(unittest.TestCase):
    task = Task(
        executors=[
            Executor(
                image="alpine",
                command=["echo", "hello"]
            )
        ]
    )
    mock_id = str(uuid.uuid4())
    mock_url = "http://fakehost:8000"
    cli = HTTPClient(mock_url, timeout=5)

    def test_cli(self):
        cli = HTTPClient(url="http://fakehost:8000//", timeout=5)
        self.assertEqual(cli.url, "http://fakehost:8000")
        self.assertAlmostEqual(cli.timeout, 5)

        with self.assertRaises(ValueError):
            HTTPClient(url="fakehost:8000", timeout=5)

        with self.assertRaises(ValueError):
            HTTPClient(url="htpp://fakehost:8000", timeout="5")  # type: ignore

    def test_create_task(self):
        with requests_mock.Mocker() as m:
            m.post(
                "%s/v1/tasks" % (self.mock_url),
                status_code=200,
                json={"id": self.mock_id}
            )
            self.cli.create_task(self.task)
            self.assertEqual(m.last_request.text, self.task.as_json())
            self.assertAlmostEqual(m.last_request.timeout, self.cli.timeout)

            m.post(
                "%s/v1/tasks" % (self.mock_url),
                status_code=500
            )
            with self.assertRaises(requests.HTTPError):
                self.cli.create_task(self.task)

            with self.assertRaises(TypeError):
                self.cli.create_task('not_a_task_object')  # type: ignore

    def test_get_task(self):
        with requests_mock.Mocker() as m:
            m.get(
                "%s/v1/tasks/%s" % (self.mock_url, self.mock_id),
                status_code=200,
                json={
                    "id": self.mock_id,
                    "state": "RUNNING",
                }
            )
            self.cli.get_task(self.mock_id, "MINIMAL")
            self.assertEqual(
                m.last_request.url,
                "%s/v1/tasks/%s?view=MINIMAL" % (self.mock_url, self.mock_id)
            )
            self.assertAlmostEqual(m.last_request.timeout, self.cli.timeout)

            m.get(
                "%s/v1/tasks/%s" % (self.mock_url, self.mock_id),
                status_code=404
            )
            with self.assertRaises(requests.HTTPError):
                self.cli.get_task(self.mock_id)

    def test_list_tasks(self):
        with requests_mock.Mocker() as m:
            m.get(
                "%s/v1/tasks" % (self.mock_url),
                status_code=200,
                json={
                    "tasks": []
                }
            )
            self.cli.list_tasks()
            self.assertEqual(
                m.last_request.url,
                "%s/v1/tasks?view=MINIMAL" % (self.mock_url)
            )
            self.assertAlmostEqual(m.last_request.timeout, self.cli.timeout)

            # empty response
            m.get(
                "%s/v1/tasks" % (self.mock_url),
                status_code=200,
                json={}
            )
            self.cli.list_tasks()
            self.assertEqual(
                m.last_request.url,
                "%s/v1/tasks?view=MINIMAL" % (self.mock_url)
            )

            m.get(
                "%s/v1/tasks" % (self.mock_url),
                status_code=500
            )
            with self.assertRaises(requests.HTTPError):
                self.cli.list_tasks()

    def test_cancel_task(self):
        with requests_mock.Mocker() as m:
            m.post(
                "%s/v1/tasks/%s:cancel" % (self.mock_url, self.mock_id),
                status_code=200,
                json={}
            )
            self.cli.cancel_task(self.mock_id)
            self.assertEqual(
                m.last_request.url,
                "%s/v1/tasks/%s:cancel" % (self.mock_url, self.mock_id)
            )
            self.assertAlmostEqual(m.last_request.timeout, self.cli.timeout)

            m.post(
                "%s/v1/tasks/%s:cancel" % (self.mock_url, self.mock_id),
                status_code=500
            )
            with self.assertRaises(requests.HTTPError):
                self.cli.cancel_task(self.mock_id)

    def test_get_service_info(self):
        with requests_mock.Mocker() as m:
            m.get(
                "%s/v1/tasks/service-info" % (self.mock_url),
                status_code=200,
                json={}
            )
            self.cli.get_service_info()
            self.assertEqual(
                m.last_request.url,
                "%s/v1/tasks/service-info" % (self.mock_url)
            )
            self.assertAlmostEqual(m.last_request.timeout, self.cli.timeout)

            m.get(
                "%s/v1/tasks/service-info" % (self.mock_url),
                status_code=500
            )
            with self.assertRaises(requests.HTTPError):
                self.cli.get_service_info()

    def test_wait(self):
        with self.assertRaises(TimeoutError):
            with requests_mock.Mocker() as m:
                m.get(
                    "%s/v1/tasks/%s" % (self.mock_url, self.mock_id),
                    status_code=200,
                    json={
                        "id": self.mock_id,
                        "state": "RUNNING",
                    }
                )
                self.cli.wait(self.mock_id, timeout=1)

        with requests_mock.Mocker() as m:
            m.get(
                "%s/v1/tasks/%s" % (self.mock_url, self.mock_id),
                [
                    {"status_code": 200,
                     "json": {"id": self.mock_id, "state": "INITIALIZING"}},
                    {"status_code": 200,
                     "json": {"id": self.mock_id, "state": "RUNNING"}},
                    {"status_code": 200,
                     "json": {"id": self.mock_id, "state": "COMPLETE"}}
                ]
            )
            self.cli.wait(self.mock_id, timeout=2)

    def test_request_params(self):

        cli = HTTPClient(url="http://fakehost:8000", timeout=5)
        vals = cli._request_params()
        self.assertAlmostEqual(vals["timeout"], 5)
        self.assertEqual(vals["headers"]["Content-type"], "application/json")
        self.assertRaises(KeyError, lambda: vals["headers"]["Authorization"])
        self.assertRaises(KeyError, lambda: vals["auth"])
        self.assertRaises(KeyError, lambda: vals["data"])
        self.assertRaises(KeyError, lambda: vals["params"])

        cli = HTTPClient(url="http://fakehost:8000", user="user",
                         password="password", token="token")
        vals = cli._request_params(data='{"json": "string"}',
                                   params={"query_param": "value"})
        self.assertAlmostEqual(vals["timeout"], 10)
        self.assertEqual(vals["headers"]["Content-type"], "application/json")
        self.assertEqual(vals["headers"]["Authorization"], "Bearer token")
        self.assertEqual(vals["auth"], ("user", "password"))
        self.assertEqual(vals["data"], '{"json": "string"}')
        self.assertEqual(vals["params"], {"query_param": "value"})
