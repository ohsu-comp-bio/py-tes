from __future__ import print_function

import polling
import requests

from urlparse import urlparse

from .models import (Task, ListTasksRequest, ListTasksResponse, ServiceInfo)
from .utils import json2obj


class HTTPClient:

    def __init__(self, url, timeout=10):
        self.url = urlparse(url).geturl()
        self.timeout = timeout

    def get_service_info(self):
        response = requests.get(
            "%s/v1/tasks/service-info" % (self.url),
            timeout=self.timeout
        )
        return json2obj(response.json(), ServiceInfo)

    def create_task(self, task):
        if task.isinstance(Task):
            msg = task.as_dict()
        else:
            raise TypeError("Expected Task instance")

        response = requests.post(
            "%s/v1/tasks" % (self.url),
            data=msg,
            timeout=self.timeout
        )
        return response.json()["id"]

    def get_task(self, task_id, view):
        payload = {"view": view}
        response = requests.get(
            "%s/v1/tasks/%s" % (self.url, task_id),
            params=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return json2obj(response.json(), Task)

    def cancel_task(self, task_id):
        response = requests.post(
            "%s/v1/tasks/%s:cancel" % (self.url, task_id),
            timeout=self.timeout
        )
        response.raise_for_status()
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
        response.raise_for_status()
        return json2obj(response.json(), ListTasksResponse)

    def wait(self, task_id, timeout=None):
        def check_success(data):
            return data["state"] not in ["QUEUED", "RUNNING", "INITIALIZING"]
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
