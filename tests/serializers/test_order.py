import pytest
from pydantic import ValidationError

from serializers.order import ReorderInput


def test_reorder_accepts_unique_ids() -> None:
    reorder = ReorderInput.model_validate({"order": [3, 1, 2]})

    assert reorder.order == [3, 1, 2]


def test_reorder_rejects_duplicate_ids() -> None:
    with pytest.raises(ValidationError, match="duplicate"):
        ReorderInput.model_validate({"order": [1, 1]})
