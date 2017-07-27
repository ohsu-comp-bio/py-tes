from __future__ import unicode_literals

import requests
import requests_mock
import unittest
import uuid

from builtins import str

from tes.client import HTTPClient
from tes.models import Task, Executor


class TestHTTPClient(unittest.TestCase):
    task = Task(
        executors=[
            Executor(
                image_name="alpine",
                cmd=["echo", "hello"]
            )
        ]
    )
    mock_id = str(uuid.uuid4())
    mock_url = "http://fakehost:8000"
    cli = HTTPClient(mock_url, timeout=5)

    def test_create_task(self):
        with requests_mock.Mocker() as m:
            m.post(
                "%s/v1/tasks" % (self.mock_url),
                status_code=200,
                json={"id": self.mock_id}
            )
            self.cli.create_task(self.task)
            self.assertEqual(m.last_request.text, self.task.as_json())
            self.assertEqual(m.last_request.timeout, self.cli.timeout)

            m.post(
                "%s/v1/tasks" % (self.mock_url),
                status_code=500
            )
            with self.assertRaises(requests.HTTPError):
                self.cli.create_task(self.task)

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
            self.assertEqual(m.last_request.timeout, self.cli.timeout)

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
            self.assertEqual(m.last_request.timeout, self.cli.timeout)

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
            self.assertEqual(m.last_request.timeout, self.cli.timeout)

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
            self.assertEqual(m.last_request.timeout, self.cli.timeout)

            m.get(
                "%s/v1/tasks/service-info" % (self.mock_url),
                status_code=500
            )
            with self.assertRaises(requests.HTTPError):
                self.cli.get_service_info()
