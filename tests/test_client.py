import pytest
import requests
import requests_mock
import unittest
import uuid

from tes.client import append_suffixes_to_url, HTTPClient, send_request
from tes.models import Task, Executor


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
        self.assertEqual(cli.url, "http://fakehost:8000//")
        self.assertEqual(cli.urls, [
            "http://fakehost:8000/ga4gh/tes/v1",
            "http://fakehost:8000/v1",
            "http://fakehost:8000"]
        )
        self.assertEqual(cli.timeout, 5)

        with self.assertRaises(TypeError):
            cli = HTTPClient(url=8000, timeout=5)  # type: ignore

        with self.assertRaises(TypeError):
            HTTPClient(url="http://fakehost:8000", timeout="5")  # type: ignore

        with self.assertRaises(ValueError):
            HTTPClient(url="fakehost:8000", timeout=5)

        with self.assertRaises(ValueError):
            HTTPClient(url="htpp://fakehost:8000", timeout=5)  # type: ignore

    def test_create_task(self):
        with requests_mock.Mocker() as m:
            m.post(
                "%s/ga4gh/tes/v1/tasks" % (self.mock_url),
                status_code=200,
                json={"id": self.mock_id}
            )
            self.cli.create_task(self.task)
            self.assertEqual(m.last_request.text, self.task.as_json())
            self.assertEqual(m.last_request.timeout, self.cli.timeout)

            m.post(
                "%s/ga4gh/tes/v1/tasks" % (self.mock_url),
                status_code=500
            )
            with self.assertRaises(requests.HTTPError):
                self.cli.create_task(self.task)

    def test_get_task(self):
        with requests_mock.Mocker() as m:
            m.get(
                "%s/ga4gh/tes/v1/tasks/%s" % (self.mock_url, self.mock_id),
                status_code=200,
                json={
                    "id": self.mock_id,
                    "state": "RUNNING",
                }
            )
            self.cli.get_task(self.mock_id, "MINIMAL")
            self.assertEqual(
                m.last_request.url,
                "%s/ga4gh/tes/v1/tasks/%s?view=MINIMAL" % (
                    self.mock_url, self.mock_id
                )
            )
            self.assertEqual(m.last_request.timeout, self.cli.timeout)

            m.get(
                requests_mock.ANY,
                status_code=404
            )
            with self.assertRaises(requests.HTTPError):
                self.cli.get_task(self.mock_id)

    def test_list_tasks(self):
        with requests_mock.Mocker() as m:
            m.get(
                "%s/ga4gh/tes/v1/tasks" % (self.mock_url),
                status_code=200,
                json={
                    "tasks": []
                }
            )
            self.cli.list_tasks()
            self.assertEqual(
                m.last_request.url,
                "%s/ga4gh/tes/v1/tasks?view=MINIMAL" % (self.mock_url)
            )
            self.assertEqual(m.last_request.timeout, self.cli.timeout)

            # empty response
            m.get(
                "%s/ga4gh/tes/v1/tasks" % (self.mock_url),
                status_code=200,
                json={}
            )
            self.cli.list_tasks()
            self.assertEqual(
                m.last_request.url,
                "%s/ga4gh/tes/v1/tasks?view=MINIMAL" % (self.mock_url)
            )

            m.get(
                "%s/ga4gh/tes/v1/tasks" % (self.mock_url),
                status_code=500
            )
            with self.assertRaises(requests.HTTPError):
                self.cli.list_tasks()

    def test_cancel_task(self):
        with requests_mock.Mocker() as m:
            m.post(
                "%s/ga4gh/tes/v1/tasks/%s:cancel" % (
                    self.mock_url, self.mock_id),
                status_code=200,
                json={}
            )
            self.cli.cancel_task(self.mock_id)
            self.assertEqual(
                m.last_request.url,
                "%s/ga4gh/tes/v1/tasks/%s:cancel" % (
                    self.mock_url, self.mock_id)
            )
            self.assertEqual(m.last_request.timeout, self.cli.timeout)

            m.post(
                "%s/ga4gh/tes/v1/tasks/%s:cancel" % (
                    self.mock_url, self.mock_id),
                status_code=500
            )
            with self.assertRaises(requests.HTTPError):
                self.cli.cancel_task(self.mock_id)

            m.post(
                requests_mock.ANY,
                status_code=404,
                json={}
            )
            with self.assertRaises(requests.HTTPError):
                self.cli.cancel_task(self.mock_id)

    def test_get_service_info(self):
        with requests_mock.Mocker() as m:
            m.get(
                "%s/ga4gh/tes/v1/service-info" % (self.mock_url),
                status_code=200,
                json={}
            )
            self.cli.get_service_info()
            self.assertEqual(
                m.last_request.url,
                "%s/ga4gh/tes/v1/service-info" % (self.mock_url)
            )
            self.assertEqual(m.last_request.timeout, self.cli.timeout)

            m.get(
                "%s/ga4gh/tes/v1/service-info" % (self.mock_url),
                status_code=500
            )
            with self.assertRaises(requests.HTTPError):
                self.cli.get_service_info()

    def test_wait(self):
        with self.assertRaises(TimeoutError):
            with requests_mock.Mocker() as m:
                m.get(
                    "%s/ga4gh/tes/v1/tasks/%s" % (self.mock_url, self.mock_id),
                    status_code=200,
                    json={
                        "id": self.mock_id,
                        "state": "RUNNING",
                    }
                )
                self.cli.wait(self.mock_id, timeout=1)

        with requests_mock.Mocker() as m:
            m.get(
                "%s/ga4gh/tes/v1/tasks/%s" % (self.mock_url, self.mock_id),
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


def test_append_suffixes_to_url():
    urls = ["http://example.com", "http://example.com/"]
    urls_order = ["http://example1.com", "http://example2.com"]
    suffixes = ["foo", "/foo", "foo/", "/foo/"]
    no_suffixes = ["", "/", "//", "///"]
    suffixes_order = ["1", "2"]

    results = append_suffixes_to_url(urls=urls, suffixes=suffixes)
    assert len(results) == len(urls) * len(suffixes)
    assert all(url == 'http://example.com/foo' for url in results)

    results = append_suffixes_to_url(urls=urls, suffixes=no_suffixes)
    assert len(results) == len(urls) * len(no_suffixes)
    assert all(url == 'http://example.com' for url in results)

    results = append_suffixes_to_url(urls=urls_order, suffixes=suffixes_order)
    assert len(results) == len(urls_order) * len(suffixes_order)
    assert results[0] == 'http://example1.com/1'
    assert results[1] == 'http://example1.com/2'
    assert results[2] == 'http://example2.com/1'
    assert results[3] == 'http://example2.com/2'


def test_send_request():
    mock_url = "http://example.com"
    mock_id = "mock_id"
    mock_urls = append_suffixes_to_url([mock_url], ["/suffix", "/"])

    # invalid method
    with pytest.raises(ValueError):
        send_request(paths=mock_urls, method="invalid")

    # errors for all paths
    with requests_mock.Mocker() as m:
        m.get(requests_mock.ANY, exc=requests.exceptions.ConnectTimeout)
        with pytest.raises(requests.HTTPError):
            send_request(paths=mock_urls)

    # error on first path, 200 on second
    with requests_mock.Mocker() as m:
        m.get(mock_urls[0], exc=requests.exceptions.ConnectTimeout)
        m.get(mock_urls[1], status_code=200)
        response = send_request(paths=mock_urls)
        assert response.status_code == 200
        assert m.last_request.url.rstrip('/') == f"{mock_url}"

    # error on first path, 404 on second
    with requests_mock.Mocker() as m:
        m.get(mock_urls[0], exc=requests.exceptions.ConnectTimeout)
        m.get(mock_urls[1], status_code=404)
        with pytest.raises(requests.HTTPError):
            send_request(paths=mock_urls)

    # 404 on first path, error on second
    with requests_mock.Mocker() as m:
        m.get(mock_urls[0], status_code=404)
        m.get(mock_urls[1], exc=requests.exceptions.ConnectTimeout)
        with pytest.raises(requests.HTTPError):
            send_request(paths=mock_urls)

    # 404 on first path, 200 on second
    with requests_mock.Mocker() as m:
        m.get(mock_urls[0], status_code=404)
        m.get(mock_urls[1], status_code=200)
        response = send_request(paths=mock_urls)
        assert response.status_code == 200
        assert m.last_request.url.rstrip('/') == f"{mock_url}"

    # POST 200
    with requests_mock.Mocker() as m:
        m.post(f"{mock_url}/suffix/foo/{mock_id}:bar", status_code=200)
        paths = append_suffixes_to_url(mock_urls, ["/foo/{id}:bar"])
        response = send_request(paths=paths, method="post", json={},
                                id=mock_id)
        assert response.status_code == 200
        assert m.last_request.url == f"{mock_url}/suffix/foo/{mock_id}:bar"

    # GET 200
    with requests_mock.Mocker() as m:
        m.get(f"{mock_url}/suffix/foo/{mock_id}", status_code=200)
        paths = append_suffixes_to_url(mock_urls, ["/foo/{id}"])
        response = send_request(paths=paths, id=mock_id)
        assert response.status_code == 200
        assert m.last_request.url == f"{mock_url}/suffix/foo/{mock_id}"

    # POST 404
    with requests_mock.Mocker() as m:
        m.post(requests_mock.ANY, status_code=404, json={})
        paths = append_suffixes_to_url(mock_urls, ["/foo"])
        with pytest.raises(requests.HTTPError):
            send_request(paths=paths, method="post", json={})
        assert m.last_request.url == f"{mock_url}/foo"

    # GET 500
    with requests_mock.Mocker() as m:
        m.get(f"{mock_url}/suffix/foo", status_code=500)
        paths = append_suffixes_to_url(mock_urls, ["/foo"])
        with pytest.raises(requests.HTTPError):
            send_request(paths=paths)
        assert m.last_request.url == f"{mock_url}/suffix/foo"
