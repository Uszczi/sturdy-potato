import re
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from use_cases.dtos import UNSET, ProjectCreateData, ProjectUpdateData

_HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")


def _normalize_color(value: object) -> object:
    """Validate a ``#rrggbb`` hex string and lower-case it; pass None through."""
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        if not _HEX_COLOR.match(value):
            raise ValueError("Color must be a '#rrggbb' hex string.")
        return value.lower()
    return value


class ProjectCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=100)
    color: str | None = Field(default=None, max_length=7)

    def to_domain(self) -> ProjectCreateData:
        return ProjectCreateData(name=self.name, color=self.color)

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("color", mode="before")
    @classmethod
    def validate_color(cls, value: object) -> object:
        return _normalize_color(value)


class ProjectUpdateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, max_length=100)
    color: str | None = Field(default=None, max_length=7)

    def to_domain(self) -> ProjectUpdateData:
        # Only provided fields become changes (exclude_unset); the name
        # validator guarantees a provided name is non-null.
        provided = self.model_fields_set

        def pick(name: str) -> Any:
            return getattr(self, name) if name in provided else UNSET

        return ProjectUpdateData(name=pick("name"), color=pick("color"))

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, value: object) -> object:
        if value is None:
            raise ValueError("Input should not be null")
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("color", mode="before")
    @classmethod
    def validate_color(cls, value: object) -> object:
        return _normalize_color(value)


class ProjectSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    color: str | None = None
    task_count: int = 0
    created_at: datetime
    updated_at: datetime
