"""Task domain model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class Task:
    """Represent a task in the domain layer."""

    id: UUID
    title: str
    created_at: datetime
    done: bool

    @classmethod
    def create(cls, title: str) -> Task:
        """Create a new task with generated identity and timestamp."""
        return cls(id=uuid4(), title=title, created_at=datetime.now(tz=UTC), done=False)
