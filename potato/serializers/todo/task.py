from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator


class TodoCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    completed: bool = False
    project_id: int | None = None

    @field_validator("title", mode="before")
    @classmethod
    def strip_title(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("project_id", mode="before")
    @classmethod
    def empty_project_is_unassigned(cls, value: object) -> object:
        return None if value == "" else value


class TodoUpdateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, max_length=200)
    description: str | None = None
    completed: bool | None = None
    project_id: int | None = None

    @field_validator("title", "description", "completed", mode="before")
    @classmethod
    def reject_null(cls, value: object) -> object:
        if value is None:
            raise ValueError("Input should not be null")
        return value

    @field_validator("project_id", mode="before")
    @classmethod
    def empty_project_is_unassigned(cls, value: object) -> object:
        return None if value == "" else value


class TodoProjectInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: int | None = None

    @field_validator("project_id", mode="before")
    @classmethod
    def empty_project_is_unassigned(cls, value: object) -> object:
        return None if value == "" else value


class TodoSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    completed: bool
    project_id: int | None
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        return value.isoformat()
