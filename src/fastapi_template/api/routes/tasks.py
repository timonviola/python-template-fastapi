"""Task routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from fastapi_template.schemas.task import TaskCreateRequest, TaskResponse
from fastapi_template.services.task_service import TaskService


def build_tasks_router(task_service: TaskService) -> APIRouter:
    """Create task routes with injected service dependency."""
    router = APIRouter(prefix="/tasks", tags=["tasks"])

    @router.get("/", response_model=list[TaskResponse])
    def list_tasks() -> list[TaskResponse]:
        """List all tasks."""
        return [TaskResponse.model_validate(task) for task in task_service.list_tasks()]

    @router.post("/", status_code=status.HTTP_201_CREATED, response_model=TaskResponse)
    def create_task(payload: TaskCreateRequest) -> TaskResponse:
        """Create one task."""
        try:
            created_task = task_service.create_task(payload.title)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

        return TaskResponse.model_validate(created_task)

    @router.post("/{task_id}/done", response_model=TaskResponse)
    def mark_task_done(task_id: UUID) -> TaskResponse:
        """Mark one task as done."""
        updated_task = task_service.mark_task_done(task_id)
        if updated_task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

        return TaskResponse.model_validate(updated_task)

    return router
