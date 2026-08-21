from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from schemas._coercions import strip_if_str


class WorkspaceCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=100)

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, value: object) -> object:
        return strip_if_str(value)


class WorkspaceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    is_personal: bool
    created_at: datetime
    updated_at: datetime
