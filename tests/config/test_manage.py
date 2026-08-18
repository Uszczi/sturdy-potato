import builtins
import runpy
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest
from manage import main


def test_manage_py_runs_check_command(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["manage.py", "check"])

    runpy.run_path(
        str(Path(__file__).parents[2] / "server" / "manage.py"),
        run_name="__main__",
    )


def test_manage_py_reports_missing_django(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        builtins,
        "__import__",
        Mock(side_effect=ImportError("Django is unavailable")),
    )

    with pytest.raises(ImportError, match="Couldn't import Django"):
        main()
