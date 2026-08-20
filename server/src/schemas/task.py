from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from schemas._coercions import empty_to_none, reject_null, strip_if_str
from use_cases.dtos import TaskCreateData, TaskUpdateData


class TaskCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    completed: bool = False
    project_id: int | None = None
    due_date: date | None = None

    def to_domain(self) -> TaskCreateData:
        return TaskCreateData(
            title=self.title,
            description=self.description,
            completed=self.completed,
            project_id=self.project_id,
            due_date=self.due_date,
        )

    @field_validator("title", mode="before")
    @classmethod
    def strip_title(cls, value: object) -> object:
        return strip_if_str(value)

    @field_validator("project_id", "due_date", mode="before")
    @classmethod
    def empty_is_unset(cls, value: object) -> object:
        return empty_to_none(value)


class TaskUpdateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, max_length=200)
    description: str | None = None
    completed: bool | None = None
    project_id: int | None = None
    due_date: date | None = None

    def to_domain(self) -> TaskUpdateData:
        # Pass only the fields the client actually sent; the rest keep their
        # UNSET default and so become non-changes (exclude_unset). Provided
        # title/description/completed are non-null thanks to the validator below.
        provided = {name: getattr(self, name) for name in self.model_fields_set}
        return TaskUpdateData(**provided)

    @field_validator("title", "description", "completed", mode="before")
    @classmethod
    def disallow_null(cls, value: object) -> object:
        return reject_null(value)

    @field_validator("project_id", "due_date", mode="before")
    @classmethod
    def empty_is_unset(cls, value: object) -> object:
        return empty_to_none(value)


class TaskCountSchema(BaseModel):
    count: int


class TaskSchema(BaseModel):
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
