import requests

from attr import attrs, attrib
from attr.validators import instance_of, optional
from urllib.parse import urlparse
from typing import Any, Dict, List, Optional

from tes.models import (Task, ListTasksRequest, ListTasksResponse, ServiceInfo,
                        GetTaskRequest, CancelTaskRequest, CreateTaskResponse,
                        strconv)
from tes.utils import unmarshal


def append_suffixes_to_url(
    urls: List[str], suffixes: List[str]
) -> List[str]:
    """Compile all combinations of full paths from paths and suffixes.

    Args:
        urls: List of URL paths.
        prefixes: List of suffixes to be appended to `urls`.

    Returns:
        List of full path combinations, in the provided order of `paths` and
        `suffixes`, starting with all suffix combinations for the first path,
        then those for the second path, and so on. Paths are stripped of any
        trailing slashes.

    Examples:
        >>> client = tes.HTTPClient.append_suffixes_to_url(['https://funnel.exa
        mple.com'], ['ga4gh/tes/v1', 'v1', ''])
        ['https://funnel.example.com/ga4gh/tes/v1', 'https://funnel.example.com
        /v1', 'https://funnel.example.com']
    """
    compiled_paths: List[str] = []
    for url in urls:
        for suffix in suffixes:
            compiled_paths.append(
                f"{url.rstrip('/')}/{suffix.strip('/')}".rstrip('/'))
    return compiled_paths


def send_request(
    paths: List[str], method: str = 'get',
    kwargs_requests: Optional[Dict[str, Any]] = None, **kwargs: Any
) -> requests.Response:
    """Send request to a list of URLs, returning the first valid response.

    Args:
        paths: List of fully qualified URLs.
        method: HTTP method to use for the request; one of 'get' (default),
            'post', 'put', and 'delete'.
        kwargs_requests: Keyword arguments to pass to the :mod:`requests` call.
        **kwargs: Keyword arguments for path parameter substition.

    Returns:
        The first successful response from the list of endpoints.

    Raises:
        requests.exceptions.HTTPError: If no response is received from any
            path.
        requests.exceptions.HTTPError: As soon as the first 4xx or 5xx status
            code is received.
        requests.exceptions.HTTPError: If, after trying all paths, at least one
            404 status code and no other 4xx or 5xx status codes are received.
        ValueError: If an unsupported HTTP method is provided.
    """
    if kwargs_requests is None:
        kwargs_requests = {}
    if method not in ('get', 'post', 'put', 'delete'):
        raise ValueError(f"Unsupported HTTP method: {method}")

    response: requests.Response = requests.Response()
    http_exceptions: Dict[str, Exception] = {}
    for path in paths:
        try:
            response = getattr(requests, method)(
                path.format(**kwargs), **kwargs_requests)
        except requests.exceptions.RequestException as exc:
            print("EXCEPTION")
            http_exceptions[path] = exc
            continue
        if response.status_code != 404:
            print("SUCCESS")
            break

    if response.status_code is None:
        raise requests.exceptions.HTTPError(
            f"No response received; HTTP Exceptions: {http_exceptions}")
    response.raise_for_status()
    return response


@attrs
class HTTPClient(object):
    url: str = attrib(validator=instance_of(str))
    timeout: int = attrib(default=10, validator=instance_of(int))
    user: Optional[str] = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str)))
    password: Optional[str] = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str)))
    token: Optional[str] = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str)))

    def __attrs_post_init__(self):
        # for backward compatibility
        self.urls: List[str] = append_suffixes_to_url(
            [self.url], ["/ga4gh/tes/v1", "/v1", "/"]
        )

    @url.validator  # type: ignore
    def __check_url(self, attribute, value):
        u = urlparse(value)
        if u.scheme not in ["http", "https"]:
            raise ValueError(
                "Unsupported URL scheme - must be one of [%s,%s]"
                % ("http", "https")
            )

    def get_service_info(self) -> ServiceInfo:
        kwargs: Dict[str, Any] = self._request_params()
        paths = append_suffixes_to_url(
            self.urls, ["service-info", "tasks/service-info"]
        )
        response = send_request(paths=paths, kwargs_requests=kwargs)
        return unmarshal(response.json(), ServiceInfo)

    def create_task(self, task: Task) -> CreateTaskResponse:
        if isinstance(task, Task):
            msg = task.as_json()
        else:
            raise TypeError("Expected Task instance")

        kwargs: Dict[str, Any] = self._request_params(data=msg)
        paths = append_suffixes_to_url(self.urls, ["/tasks"])
        response = send_request(paths=paths, method='post',
                                kwargs_requests=kwargs)
        return unmarshal(response.json(), CreateTaskResponse).id

    def get_task(self, task_id: str, view: str = "BASIC") -> Task:
        req: GetTaskRequest = GetTaskRequest(task_id, view)
        payload: Dict[str, Optional[str]] = {"view": req.view}
        kwargs: Dict[str, Any] = self._request_params(params=payload)
        paths = append_suffixes_to_url(self.urls, ["/tasks/{task_id}"])
        response = send_request(paths=paths, kwargs_requests=kwargs,
                                task_id=req.id)
        return unmarshal(response.json(), Task)

    def cancel_task(self, task_id: str) -> None:
        req: CancelTaskRequest = CancelTaskRequest(task_id)
        kwargs: Dict[str, Any] = self._request_params()
        paths = append_suffixes_to_url(self.urls, ["/tasks/{task_id}:cancel"])
        send_request(paths=paths, method='post', kwargs_requests=kwargs,
                     task_id=req.id)
        return None

    def list_tasks(
        self, view: str = "MINIMAL", page_size: Optional[int] = None,
        page_token: Optional[str] = None
    ) -> ListTasksResponse:
        req = ListTasksRequest(
            view=view,
            page_size=page_size,
            page_token=page_token,
            name_prefix=None,
            project=None
        )
        msg: Dict = req.as_dict()

        kwargs: Dict[str, Any] = self._request_params(params=msg)
        paths = append_suffixes_to_url(self.urls, ["/tasks"])
        response = send_request(paths=paths, kwargs_requests=kwargs)
        return unmarshal(response.json(), ListTasksResponse)

    def _request_params(
        self, data: Optional[str] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {}
        kwargs['timeout'] = self.timeout
        kwargs['headers'] = {}
        kwargs['headers']['Content-type'] = 'application/json'
        kwargs['auth'] = (self.user, self.password)
        if data:
            kwargs['data'] = data
        if params:
            kwargs['params'] = params
        if self.token:
            kwargs['headers']['Authorization'] = f"Bearer {self.token}"
        return kwargs
