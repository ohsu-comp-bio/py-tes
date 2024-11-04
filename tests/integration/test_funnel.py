import pytest
import tes


@pytest.fixture
def tes_client():
    return tes.HTTPClient("http://localhost:8000", timeout=5)


@pytest.fixture
def task():
    return tes.Task(
        executors=[
            tes.Executor(
                image="alpine",
                command=["echo", "hello"]
            )
        ]
    )


def test_service_info(tes_client):
    service_info = tes_client.get_service_info()
    assert service_info is not None


def test_task_creation(tes_client, task):
    task_id = tes_client.create_task(task)
    assert task_id is not None

    _ = tes_client.wait(task_id)

    task_info = tes_client.get_task(task_id, view="BASIC")
    assert task_info is not None


def test_task_status(tes_client, task):
    task_id = tes_client.create_task(task)
    assert task_id is not None

    status = tes_client.get_task(task_id, view="MINIMAL").state
    assert status in ["QUEUED", "INITIALIZING", "RUNNING", "COMPLETE", "CANCELED", "EXECUTOR_ERROR", "SYSTEM_ERROR", "UNKNOWN"]


def test_task_logs(tes_client, task):
    task_id = tes_client.create_task(task)
    assert task_id is not None

    _ = tes_client.wait(task_id)

    logs = tes_client.get_task(task_id, view="FULL").logs
    assert logs is not None
    assert len(logs) > 0
