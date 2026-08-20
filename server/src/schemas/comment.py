from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from schemas._coercions import strip_if_str
from use_cases.dtos import CommentCreateData, CommentUpdateData


class CommentCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    body: str = Field(min_length=1, max_length=2000)

    def to_domain(self) -> CommentCreateData:
        return CommentCreateData(body=self.body)

    @field_validator("body", mode="before")
    @classmethod
    def strip_body(cls, value: object) -> object:
        return strip_if_str(value)


class CommentUpdateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Editing replaces the single field, so ``body`` is required here (unlike the
    # partial task update, there is nothing else to leave untouched).
    body: str = Field(min_length=1, max_length=2000)

    def to_domain(self) -> CommentUpdateData:
        return CommentUpdateData(body=self.body)

    @field_validator("body", mode="before")
    @classmethod
    def strip_body(cls, value: object) -> object:
        return strip_if_str(value)


class CommentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    body: str
    created_at: datetime
    updated_at: datetime
