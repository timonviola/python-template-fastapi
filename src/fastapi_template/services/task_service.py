"""Task service orchestration."""

from __future__ import annotations

from uuid import UUID

from fastapi_template.domain.task import Task
from fastapi_template.repositories.task_repository import TaskRepository


class TaskService:
    """Expose task use-cases."""

    def __init__(self, repository: TaskRepository) -> None:
        """Build service from repository implementation."""
        self._repository: TaskRepository = repository

    def list_tasks(self) -> list[Task]:
        """Return all tasks."""
        return self._repository.list()

    def create_task(self, title: str) -> Task:
        """Create and persist a task from a title."""
        normalized_title = title.strip()
        if not normalized_title:
            msg = "Task title cannot be blank."
            raise ValueError(msg)

        return self._repository.add(Task.create(normalized_title))

    def mark_task_done(self, task_id: UUID) -> Task | None:
        """Mark one task as done."""
        return self._repository.mark_done(task_id)
