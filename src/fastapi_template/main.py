"""FastAPI application entrypoint."""

from __future__ import annotations

from importlib.metadata import version

import uvicorn
from fastapi import FastAPI

from fastapi_template.api.routes.tasks import build_tasks_router
from fastapi_template.config import AppConfig, load_config
from fastapi_template.observability import configure_logging, configure_tracing
from fastapi_template.repositories.in_memory_task_repository import InMemoryTaskRepository
from fastapi_template.services.task_service import TaskService

configure_logging()

APP_CONFIG = load_config()
APP_VERSION = version("fastapi-template")


def create_app(task_service: TaskService | None = None, config: AppConfig | None = None) -> FastAPI:
    """Build and configure the FastAPI application."""
    resolved_task_service: TaskService
    if task_service is None:
        resolved_task_service = TaskService(InMemoryTaskRepository())
    else:
        resolved_task_service = task_service

    resolved_config = APP_CONFIG if config is None else config

    app = FastAPI(
        title="FastAPI Template",
        version=APP_VERSION,
        description="Template app with strict typing and repository pattern.",
    )

    configure_tracing(app)

    app.include_router(build_tasks_router(resolved_task_service), prefix=resolved_config.api_prefix)

    @app.get(f"{resolved_config.api_prefix}/healthz")
    def healthz() -> dict[str, str]:
        """Return healthcheck status."""
        return {"status": "ok"}

    return app


def run_dev() -> None:
    """Run a development server with auto-reload."""
    uvicorn.run(
        "fastapi_template.main:app",
        host=APP_CONFIG.host,
        port=APP_CONFIG.port,
        reload=True,
    )


app = create_app(config=APP_CONFIG)
