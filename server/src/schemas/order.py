from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReorderInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order: list[int] = Field(min_length=0)

    @field_validator("order")
    @classmethod
    def order_contains_unique_ids(cls, value: list[int]) -> list[int]:
        if len(value) != len(set(value)):
            raise ValueError("Order contains duplicate IDs.")
        return value
