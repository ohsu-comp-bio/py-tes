from __future__ import absolute_import, print_function, unicode_literals

import polling
import requests

from attr import attrs, attrib
from attr.validators import instance_of
from requests.utils import urlparse

from tes.models import (Task, ListTasksRequest, ListTasksResponse, ServiceInfo,
                        GetTaskRequest, CancelTaskRequest, CreateTaskResponse)
from tes.utils import unmarshal, raise_for_status


@attrs
class HTTPClient(object):
    url = attrib()
    timeout = attrib(default=10, validator=instance_of(int))

    @url.validator
    def __check_url(self, attribute, value):
        u = urlparse(value)
        if u.scheme not in ["http", "https"]:
            raise ValueError(
                "Unsupported URL scheme - must be one of %s"
                % (["http", "https"])
            )

    def get_service_info(self):
        response = requests.get(
            "%s/v1/tasks/service-info" % (self.url),
            timeout=self.timeout
        )
        raise_for_status(response)
        return unmarshal(response.json(), ServiceInfo)

    def create_task(self, task):
        if isinstance(task, Task):
            msg = task.as_json()
        else:
            raise TypeError("Expected Task instance")
        response = requests.post(
            "%s/v1/tasks" % (self.url),
            data=msg,
            timeout=self.timeout
        )
        raise_for_status(response)
        return unmarshal(response.json(), CreateTaskResponse).id

    def get_task(self, task_id, view="BASIC"):
        req = GetTaskRequest(task_id, view)
        payload = {"view": req.view}
        response = requests.get(
            "%s/v1/tasks/%s" % (self.url, req.id),
            params=payload,
            timeout=self.timeout
        )
        raise_for_status(response)
        return unmarshal(response.json(), Task)

    def cancel_task(self, task_id):
        req = CancelTaskRequest(task_id)
        response = requests.post(
            "%s/v1/tasks/%s:cancel" % (self.url, req.id),
            timeout=self.timeout
        )
        raise_for_status(response)
        return

    def list_tasks(self, view="MINIMAL", page_size=None, page_token=None):
        req = ListTasksRequest(
            view=view,
            page_size=page_size,
            page_token=page_token,
            name_prefix=None,
            project=None
        )
        msg = req.as_dict()

        response = requests.get(
            "%s/v1/tasks" % (self.url),
            params=msg,
            timeout=self.timeout
        )
        raise_for_status(response)
        return unmarshal(response.json(), ListTasksResponse)

    def wait(self, task_id, timeout=None):
        def check_success(data):
            return data.state not in ["QUEUED", "RUNNING", "INITIALIZING"]
        if timeout is not None:
            return polling.poll(
                lambda: self.get_task(task_id, "MINIMAL"),
                check_success=check_success,
                timeout=timeout,
                step=0.1
            )
        return polling.poll(
            lambda: self.get_task(task_id, "MINIMAL"),
            check_success=check_success,
            step=0.1,
            poll_forever=True
        )
