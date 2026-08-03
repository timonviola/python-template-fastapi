"""Task HTTP schemas."""

from __future__ import annotations

from datetime import datetime
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaskCreateRequest(BaseModel):
    """Represent API payload for task creation."""

    title: str = Field(min_length=1, max_length=200)


class TaskResponse(BaseModel):
    """Represent API response payload for tasks."""

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    created_at: datetime
    done: bool
