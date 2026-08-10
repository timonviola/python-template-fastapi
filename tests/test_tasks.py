"""Task endpoint tests."""

from uuid import uuid4

from fastapi.testclient import TestClient

from fastapi_template.config import AppConfig
from fastapi_template.main import create_app
from fastapi_template.repositories.in_memory_task_repository import InMemoryTaskRepository
from fastapi_template.services.task_service import TaskService


def _create_client() -> TestClient:
    service = TaskService(InMemoryTaskRepository())
    config = AppConfig(host="127.0.0.1", port=8000, api_prefix="/v1")
    return TestClient(create_app(task_service=service, config=config))


def test_create_and_list_tasks() -> None:
    client = _create_client()

    create_response = client.post("/v1/tasks/", json={"title": "Write tests"})
    assert create_response.status_code == 201

    list_response = client.get("/v1/tasks/")
    assert list_response.status_code == 200

    tasks = list_response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Write tests"
    assert tasks[0]["done"] is False


def test_mark_task_done() -> None:
    client = _create_client()

    create_response = client.post("/v1/tasks/", json={"title": "Ship release"})
    created_task = create_response.json()

    mark_done_response = client.post(f"/v1/tasks/{created_task['id']}/done")
    assert mark_done_response.status_code == 200
    assert mark_done_response.json()["done"] is True


def test_create_task_with_blank_title_returns_400() -> None:
    client = _create_client()

    response = client.post("/v1/tasks/", json={"title": "   "})

    assert response.status_code == 400
    assert response.json()["detail"] == "Task title cannot be blank."


def test_mark_unknown_task_done_returns_404() -> None:
    client = _create_client()

    response = client.post(f"/v1/tasks/{uuid4()}/done")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found."
