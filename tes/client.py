from __future__ import print_function

import polling
import requests

from urlparse import urlparse

from .models import (Task, ListTasksRequest, ListTaskResponse, ServiceInfo)
from .utils import json2obj


class TESClient:

    def __init__(self, url, timeout=10):
        n = urlparse(url)
        self.url = n.geturl()
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

    def wait(self, task_id, timeout=30):
        def check_success(data):
            return data["state"] not in ["QUEUED", "RUNNING", "INITIALIZING"]
        return polling.poll(
            lambda: self.get_task(task_id, "MINIMAL"),
            check_success=check_success,
            timeout=timeout,
            step=0.1
        )

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

    def list_tasks(self, req):
        if req.isinstance(ListTasksRequest):
            msg = req.as_dict()
        else:
            raise TypeError("Expected ListTasksRequest instance")

        response = requests.get(
            "%s/v1/tasks" % (self.url),
            params=msg,
            timeout=self.timeout
        )
        response.raise_for_status()
        return json2obj(response.json(), ListTaskResponse)
