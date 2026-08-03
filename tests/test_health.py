"""Healthcheck tests."""

from fastapi.testclient import TestClient

from fastapi_template.config import AppConfig
from fastapi_template.main import create_app
from fastapi_template.repositories.in_memory_task_repository import InMemoryTaskRepository
from fastapi_template.services.task_service import TaskService


def test_healthz_returns_ok() -> None:
    service = TaskService(InMemoryTaskRepository())
    config = AppConfig(host="127.0.0.1", port=8000, api_prefix="/v1")
    client = TestClient(create_app(task_service=service, config=config))

    response = client.get("/v1/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
