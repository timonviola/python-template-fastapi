"""Task repository protocol."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from fastapi_template.domain.task import Task


class TaskRepository(Protocol):
    """Describe required persistence operations for tasks."""

    def list(self) -> list[Task]:
        """Return all tasks."""
        ...

    def get(self, task_id: UUID) -> Task | None:
        """Return a task by id."""
        ...

    def add(self, task: Task) -> Task:
        """Persist and return a task."""
        ...

    def mark_done(self, task_id: UUID) -> Task | None:
        """Mark a task as done and return the updated task."""
        ...
