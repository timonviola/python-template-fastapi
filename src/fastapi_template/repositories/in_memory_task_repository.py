"""In-memory task repository implementation."""

from __future__ import annotations

from dataclasses import replace
from typing import override
from uuid import UUID

from fastapi_template.domain.task import Task
from fastapi_template.repositories.task_repository import TaskRepository


class InMemoryTaskRepository(TaskRepository):
    """Persist tasks in process memory."""

    def __init__(self) -> None:
        """Initialize empty storage."""
        self._tasks: dict[UUID, Task] = {}

    @override
    def list(self) -> list[Task]:
        """Return all tasks in insertion order."""
        return list(self._tasks.values())

    @override
    def get(self, task_id: UUID) -> Task | None:
        """Return one task if present."""
        return self._tasks.get(task_id)

    @override
    def add(self, task: Task) -> Task:
        """Insert a task and return it."""
        self._tasks[task.id] = task
        return task

    @override
    def mark_done(self, task_id: UUID) -> Task | None:
        """Set done to true for a task, if it exists."""
        task = self._tasks.get(task_id)
        if task is None:
            return None

        updated = replace(task, done=True)
        self._tasks[task_id] = updated
        return updated
