import json
from collections.abc import Callable
from pathlib import Path
from typing import cast

import pytest

SNAPSHOT_DIR = Path(__file__).parent / "snapshots"


@pytest.fixture
def load_snapshot() -> Callable[[str], object]:
    def _load_snapshot(filename: str) -> object:
        return cast(
            object,
            json.loads((SNAPSHOT_DIR / filename).read_text(encoding="utf-8")),
        )

    return _load_snapshot
