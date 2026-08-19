from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TodoCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    completed: bool = False
    project_id: int | None = None
    due_date: date | None = None

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

    @field_validator("due_date", mode="before")
    @classmethod
    def empty_due_date_is_unset(cls, value: object) -> object:
        return None if value == "" else value


class TodoUpdateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, max_length=200)
    description: str | None = None
    completed: bool | None = None
    project_id: int | None = None
    due_date: date | None = None

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

    @field_validator("due_date", mode="before")
    @classmethod
    def empty_due_date_is_unset(cls, value: object) -> object:
        return None if value == "" else value


class TaskCountSchema(BaseModel):
    count: int


class TodoSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    completed: bool
    position: int
    project_id: int | None
    due_date: date | None
    created_at: datetime
    updated_at: datetime
