from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from schemas._coercions import empty_to_none, reject_null, strip_if_str
from use_cases.dtos import TaskCreateData, TaskUpdateData
from use_cases.workflow import MAX_KEY_LENGTH


class TaskCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    # A status key from the target board's workflow. Omitted means "wherever
    # this board starts", which is what a plain new task wants.
    status: str | None = Field(default=None, max_length=MAX_KEY_LENGTH)
    project_id: int | None = None
    due_date: date | None = None

    def to_domain(self) -> TaskCreateData:
        return TaskCreateData(
            title=self.title,
            description=self.description,
            status=self.status,
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
    status: str | None = Field(default=None, max_length=MAX_KEY_LENGTH)
    project_id: int | None = None
    due_date: date | None = None

    def to_domain(self) -> TaskUpdateData:
        # Pass only the fields the client actually sent; the rest keep their
        # UNSET default and so become non-changes (exclude_unset). Provided
        # title/description/status are non-null thanks to the validator below.
        provided = {name: getattr(self, name) for name in self.model_fields_set}
        return TaskUpdateData(**provided)

    @field_validator("title", "description", "status", mode="before")
    @classmethod
    def disallow_null(cls, value: object) -> object:
        return reject_null(value)

    @field_validator("project_id", "due_date", mode="before")
    @classmethod
    def empty_is_unset(cls, value: object) -> object:
        return empty_to_none(value)


class TaskMoveInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # The column the card lands in and its index within that column (0 = top).
    status: str = Field(min_length=1, max_length=MAX_KEY_LENGTH)
    position: int = Field(ge=0)


class TaskCountSchema(BaseModel):
    count: int


class TaskSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    status: str
    # Whether ``status`` is terminal on this task's board. The client can't
    # derive it: the same key can be terminal in one project and not another.
    is_done: bool
    position: int
    project_id: int | None
    due_date: date | None
    created_at: datetime
    updated_at: datetime
