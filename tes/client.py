"""TES access methods and helper functions."""

import re
import requests
import time

from attr import attrs, attrib
from attr.validators import instance_of, optional
from urllib.parse import urlparse
from typing import Any, Dict, Optional

from tes.models import (Task, ListTasksRequest, ListTasksResponse, ServiceInfo,
                        GetTaskRequest, CancelTaskRequest, CreateTaskResponse,
                        strconv)
from tes.utils import unmarshal, TimeoutError


def process_url(value):
    return re.sub("[/]+$", "", value)


@attrs
class HTTPClient(object):
    """HTTP client class for interacting with the TES API."""
    url: str = attrib(converter=process_url)
    timeout: int = attrib(default=10, validator=instance_of(int))
    user: Optional[str] = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str)))
    password: Optional[str] = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str)))
    token: Optional[str] = attrib(
        default=None, converter=strconv, validator=optional(instance_of(str)))

    @url.validator  # type: ignore
    def __check_url(self, attribute, value):
        """Validate URL scheme of TES instance.

        `attrs` validator function for `HTTPClient.url`.

        Args:
            attribute: Attribute being validated.
            value: Attribute value.

        Raises:
            ValueError: If URL scheme is unsupported.
        """
        u = urlparse(value)
        if u.scheme not in ["http", "https"]:
            raise ValueError(
                "Unsupported URL scheme - must be one of [%s,%s]"
                % ("http", "https")
            )

    def get_service_info(self) -> ServiceInfo:
        """Access method for `GET /service-info`.

        Returns:
            `tes.models.ServiceInfo` instance.
        """
        kwargs: Dict[str, Any] = self._request_params()
        response: requests.Response = requests.get(
            f"{self.url}/v1/tasks/service-info",
            **kwargs)
        response.raise_for_status()
        return unmarshal(response.json(), ServiceInfo)

    def create_task(self, task: Task) -> CreateTaskResponse:
        """Access method for `POST /tasks`.

        Args:
            task: `tes.models.Task` instance.

        Returns:
            `tes.models.CreateTaskResponse` instance.

        Raises:
            TypeError: If `task` is not a `tes.models.Task` instance.
        """
        if isinstance(task, Task):
            msg = task.as_json()
        else:
            raise TypeError("Expected Task instance")

        kwargs: Dict[str, Any] = self._request_params(data=msg)
        response: requests.Response = requests.post(
            f"{self.url}/v1/tasks",
            **kwargs
        )
        response.raise_for_status()
        return unmarshal(response.json(), CreateTaskResponse).id

    def get_task(self, task_id: str, view: str = "BASIC") -> Task:
        """Access method for `GET /tasks/{id}`.

        Args:
            task_id: TES Task ID.
            view: Task info verbosity. One of `MINIMAL`, `BASIC` and `FULL`.

        Returns:
            `tes.models.Task` instance.
        """
        req: GetTaskRequest = GetTaskRequest(task_id, view)
        payload: Dict[str, Optional[str]] = {"view": req.view}
        kwargs: Dict[str, Any] = self._request_params(params=payload)
        response: requests.Response = requests.get(
            f"{self.url}/v1/tasks/{req.id}",
            **kwargs)
        response.raise_for_status()
        return unmarshal(response.json(), Task)

    def cancel_task(self, task_id: str) -> None:
        """Access method for `POST /tasks/{id}:cancel`.

        Args:
            task_id: TES Task ID.
        """
        req: CancelTaskRequest = CancelTaskRequest(task_id)
        kwargs: Dict[str, Any] = self._request_params()
        response: requests.Response = requests.post(
            f"{self.url}/v1/tasks/{req.id}:cancel",
            **kwargs)
        response.raise_for_status()
        return None

    def list_tasks(
        self, view: str = "MINIMAL", page_size: Optional[int] = None,
        page_token: Optional[str] = None
    ) -> ListTasksResponse:
        """Access method for `GET /tasks`.

        Args:
            view: Task info verbosity. One of `MINIMAL`, `BASIC` and `FULL`.
            page_size: Number of tasks to return.
            page_token: Token to retrieve the next page of tasks.

        Returns:
            `tes.models.ListTasksResponse` instance.
        """
        req = ListTasksRequest(
            view=view,
            page_size=page_size,
            page_token=page_token,
            name_prefix=None,
            project=None
        )
        msg: Dict = req.as_dict()

        kwargs: Dict[str, Any] = self._request_params(params=msg)
        response: requests.Response = requests.get(
            f"{self.url}/v1/tasks",
            **kwargs)
        response.raise_for_status()
        return unmarshal(response.json(), ListTasksResponse)

    def wait(self, task_id: str, timeout=None) -> Task:
        def check_success(data: Task) -> bool:
            return data.state not in ["QUEUED", "RUNNING", "INITIALIZING"]

        max_time = time.time() + timeout if timeout else None

        response: Optional[Task] = None
        while True:
            try:
                response = self.get_task(task_id, "MINIMAL")
            except Exception:
                pass

            if response is not None:
                if check_success(response):
                    return response

                if max_time is not None and time.time() >= max_time:
                    raise TimeoutError("last_response: {response.as_dict()}")
            time.sleep(0.5)

    def _request_params(
        self, data: Optional[str] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Compile request parameters.

        Args:
            data: JSON payload to be sent in the request body.

        Returns:
            Dictionary of request parameters.
        """
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
