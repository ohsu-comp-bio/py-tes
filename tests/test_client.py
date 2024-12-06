import pytest
import requests
import requests_mock
import uuid

from tes.client import append_suffixes_to_url, HTTPClient, send_request
from tes.models import Task, Executor
from tes.utils import TimeoutError


@pytest.fixture
def task():
    return Task(executors=[Executor(image="alpine", command=["echo", "hello"])])


@pytest.fixture
def mock_id():
    return str(uuid.uuid4())


@pytest.fixture
def mock_url():
    return "http://fakehost:8000"


@pytest.fixture
def cli(mock_url):
    return HTTPClient(mock_url, timeout=5)


def test_cli():
    cli = HTTPClient(url="http://fakehost:8000//", timeout=5)
    assert cli.url == "http://fakehost:8000"
    assert cli.urls == [
        "http://fakehost:8000/ga4gh/tes/v1",
        "http://fakehost:8000/v1",
        "http://fakehost:8000",
    ]
    assert cli.timeout == 5

    with pytest.raises(TypeError):
        HTTPClient(url=8000, timeout=5)  # type: ignore

    with pytest.raises(TypeError):
        HTTPClient(url="http://fakehost:8000", timeout="5")  # type: ignore

    with pytest.raises(ValueError):
        HTTPClient(url="fakehost:8000", timeout=5)

    with pytest.raises(ValueError):
        HTTPClient(url="htpp://fakehost:8000", timeout=5)  # type: ignore


def test_create_task(cli, task, mock_id, mock_url):
    with requests_mock.Mocker() as m:
        m.post(f"{mock_url}/ga4gh/tes/v1/tasks", status_code=200, json={"id": mock_id})
        cli.create_task(task)
        assert m.last_request.text == task.as_json()
        assert m.last_request.timeout == cli.timeout

        m.post(f"{mock_url}/ga4gh/tes/v1/tasks", status_code=500)
        with pytest.raises(requests.HTTPError):
            cli.create_task(task)

        with pytest.raises(TypeError):
            cli.create_task("not_a_task_object")  # type: ignore


def test_get_task(cli, mock_id, mock_url):
    with requests_mock.Mocker() as m:
        m.get(
            f"{mock_url}/ga4gh/tes/v1/tasks/{mock_id}",
            status_code=200,
            json={
                "id": mock_id,
                "state": "RUNNING",
            },
        )
        cli.get_task(mock_id, "MINIMAL")
        assert (
            m.last_request.url
            == f"{mock_url}/ga4gh/tes/v1/tasks/{mock_id}?view=MINIMAL"
        )
        assert m.last_request.timeout == cli.timeout

        m.get(requests_mock.ANY, status_code=404)
        with pytest.raises(requests.HTTPError):
            cli.get_task(mock_id)


def test_list_tasks(cli, mock_url):
    with requests_mock.Mocker() as m:
        m.get(f"{mock_url}/ga4gh/tes/v1/tasks", status_code=200, json={"tasks": []})
        cli.list_tasks()
        assert m.last_request.url == f"{mock_url}/ga4gh/tes/v1/tasks?view=MINIMAL"
        assert m.last_request.timeout == cli.timeout

        # empty response
        m.get(f"{mock_url}/ga4gh/tes/v1/tasks", status_code=200, json={})
        cli.list_tasks()
        assert m.last_request.url == f"{mock_url}/ga4gh/tes/v1/tasks?view=MINIMAL"

        m.get(f"{mock_url}/ga4gh/tes/v1/tasks", status_code=500)
        with pytest.raises(requests.HTTPError):
            cli.list_tasks()


def test_cancel_task(cli, mock_id, mock_url):
    with requests_mock.Mocker() as m:
        m.post(
            f"{mock_url}/ga4gh/tes/v1/tasks/{mock_id}:cancel", status_code=200, json={}
        )
        cli.cancel_task(mock_id)
        assert m.last_request.url == f"{mock_url}/ga4gh/tes/v1/tasks/{mock_id}:cancel"
        assert m.last_request.timeout == cli.timeout

        m.post(f"{mock_url}/ga4gh/tes/v1/tasks/{mock_id}:cancel", status_code=500)
        with pytest.raises(requests.HTTPError):
            cli.cancel_task(mock_id)

        m.post(requests_mock.ANY, status_code=404, json={})
        with pytest.raises(requests.HTTPError):
            cli.cancel_task(mock_id)


def test_get_service_info(cli, mock_url):
    with requests_mock.Mocker() as m:
        m.get(f"{mock_url}/ga4gh/tes/v1/service-info", status_code=200, json={})
        cli.get_service_info()
        assert m.last_request.url == f"{mock_url}/ga4gh/tes/v1/service-info"
        assert m.last_request.timeout == cli.timeout

        m.get(f"{mock_url}/ga4gh/tes/v1/service-info", status_code=500)
        with pytest.raises(requests.HTTPError):
            cli.get_service_info()


def test_wait(cli, mock_id, mock_url):
    with pytest.raises(TimeoutError):
        with requests_mock.Mocker() as m:
            m.get(
                f"{mock_url}/ga4gh/tes/v1/tasks/{mock_id}",
                status_code=200,
                json={
                    "id": mock_id,
                    "state": "RUNNING",
                },
            )
            cli.wait(mock_id, timeout=1)

    with requests_mock.Mocker() as m:
        m.get(
            f"{mock_url}/ga4gh/tes/v1/tasks/{mock_id}",
            [
                {"status_code": 200, "json": {"id": mock_id, "state": "INITIALIZING"}},
                {"status_code": 200, "json": {"id": mock_id, "state": "RUNNING"}},
                {"status_code": 200, "json": {"id": mock_id, "state": "COMPLETE"}},
            ],
        )
        cli.wait(mock_id, timeout=2)


def test_wait_exception(cli, mock_id, mock_url):
    with requests_mock.Mocker() as m:
        m.get(
            f"{mock_url}/ga4gh/tes/v1/tasks/{mock_id}",
            status_code=200,
            json={
                "Error": "Error",
            },
        )
        with pytest.raises(Exception):
            cli.wait(mock_id, timeout=2)


def test_wait_no_state_change(cli, mock_id, mock_url):
    with requests_mock.Mocker() as m:
        m.get(
            f"{mock_url}/ga4gh/tes/v1/tasks/{mock_id}",
            [
                {"status_code": 200, "json": {"id": mock_id, "state": "RUNNING"}},
                {"status_code": 200, "json": {"id": mock_id, "state": "RUNNING"}},
                # Continues to return RUNNING state
            ],
        )
        with pytest.raises(TimeoutError):
            cli.wait(mock_id, timeout=2)


def test_request_params():
    cli = HTTPClient(url="http://fakehost:8000", timeout=5)
    vals = cli._request_params()
    assert vals["timeout"] == 5
    assert vals["headers"]["Content-type"] == "application/json"
    with pytest.raises(KeyError):
        _ = vals["headers"]["Authorization"]
    with pytest.raises(KeyError):
        _ = vals["auth"]
    with pytest.raises(KeyError):
        _ = vals["data"]
    with pytest.raises(KeyError):
        _ = vals["params"]

    cli = HTTPClient(
        url="http://fakehost:8000", user="user", password="password", token="token"
    )
    vals = cli._request_params(
        data='{"json": "string"}', params={"query_param": "value"}
    )
    assert vals["timeout"] == 10
    assert vals["headers"]["Content-type"] == "application/json"
    assert vals["headers"]["Authorization"] == "Bearer token"
    assert vals["auth"] == ("user", "password")
    assert vals["data"] == '{"json": "string"}'
    assert vals["params"] == {"query_param": "value"}


def test_append_suffixes_to_url():
    urls = ["http://example.com", "http://example.com/"]
    urls_order = ["http://example1.com", "http://example2.com"]
    suffixes = ["foo", "/foo", "foo/", "/foo/"]
    no_suffixes = ["", "/", "//", "///"]
    suffixes_order = ["1", "2"]

    results = append_suffixes_to_url(urls=urls, suffixes=suffixes)
    assert len(results) == len(urls) * len(suffixes)
    assert all(url == "http://example.com/foo" for url in results)

    results = append_suffixes_to_url(urls=urls, suffixes=no_suffixes)
    assert len(results) == len(urls) * len(no_suffixes)
    assert all(url == "http://example.com" for url in results)

    results = append_suffixes_to_url(urls=urls_order, suffixes=suffixes_order)
    assert len(results) == len(urls_order) * len(suffixes_order)
    assert results[0] == "http://example1.com/1"
    assert results[1] == "http://example1.com/2"
    assert results[2] == "http://example2.com/1"
    assert results[3] == "http://example2.com/2"


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
        assert m.last_request.url.rstrip("/") == f"{mock_url}"

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
        assert m.last_request.url.rstrip("/") == f"{mock_url}"

    # POST 200
    with requests_mock.Mocker() as m:
        m.post(f"{mock_url}/suffix/foo/{mock_id}:bar", status_code=200)
        paths = append_suffixes_to_url(mock_urls, ["/foo/{id}:bar"])
        response = send_request(paths=paths, method="post", json={}, id=mock_id)
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
