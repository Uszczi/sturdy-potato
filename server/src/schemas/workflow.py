from pydantic import BaseModel, ConfigDict, Field, field_validator

from schemas._coercions import strip_if_str
from use_cases.dtos import WorkflowUpdateData
from use_cases.workflow import MAX_KEY_LENGTH, MAX_LABEL_LENGTH, Status, Workflow


class StatusSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    label: str
    is_initial: bool
    is_terminal: bool


class WorkflowMixin(BaseModel):
    """Adds a board's ordered statuses to a detail response.

    The entity carries a ``Workflow``; the wire format is the plain ordered list,
    since list order is the column order.
    """

    workflow: list[StatusSchema]

    @field_validator("workflow", mode="before")
    @classmethod
    def unwrap_workflow(cls, value: object) -> object:
        return value.statuses if isinstance(value, Workflow) else value


class StatusInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(min_length=1, max_length=MAX_KEY_LENGTH)
    label: str = Field(min_length=1, max_length=MAX_LABEL_LENGTH)
    is_initial: bool = False
    is_terminal: bool = False

    @field_validator("label", mode="before")
    @classmethod
    def strip_label(cls, value: object) -> object:
        return strip_if_str(value)


class WorkflowInput(BaseModel):
    """The complete desired workflow for one board.

    Beyond field shapes, the rules that make a workflow valid (how many statuses,
    exactly one initial, at least one terminal) live in the domain, so a bad
    workflow fails the same way whether it arrives over HTTP or from the CLI.
    """

    model_config = ConfigDict(extra="forbid")

    statuses: list[StatusInput]
    # Status key being removed -> the key its tasks move to. Required for every
    # key this request drops from the workflow.
    reassign: dict[str, str] = Field(default_factory=dict)

    def to_domain(self) -> WorkflowUpdateData:
        return WorkflowUpdateData(
            statuses=tuple(
                Status(
                    key=status.key,
                    label=status.label,
                    is_initial=status.is_initial,
                    is_terminal=status.is_terminal,
                )
                for status in self.statuses
            ),
            reassign=self.reassign,
        )
