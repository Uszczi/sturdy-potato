import importlib
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

import main
from config import settings


@pytest.mark.asyncio
async def test_frontend_served_when_dist_present(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # In production the built SPA lives in frontend_dir; main.py mounts it at
    # import time. Point frontend_dir at a directory holding a built index.html
    # and reload main so the mounting branch runs, then confirm it is served.
    (tmp_path / "index.html").write_text("<!doctype html><title>app</title>")
    monkeypatch.setattr(settings, "frontend_dir", tmp_path)
    try:
        reloaded = importlib.reload(main)
        transport = ASGITransport(app=reloaded.app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/")
        assert response.status_code == 200
        assert "<title>app</title>" in response.text
    finally:
        # Restore the module for other tests that imported `app` from it.
        importlib.reload(main)
