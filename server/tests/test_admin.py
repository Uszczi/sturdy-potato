from typing import cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.requests import Request

import infrastructure.admin as admin_module
from infrastructure.admin import AdminAuth
from tests.factories import create_user

PASSWORD = "pw-123"


class FakeRequest:
    def __init__(
        self, form: dict[str, str], session: dict[str, str] | None = None
    ) -> None:
        self._form = form
        self.session: dict[str, str] = {} if session is None else session

    async def form(self) -> dict[str, str]:
        return self._form


@pytest.fixture
def backend() -> AdminAuth:
    return AdminAuth(secret_key="test-secret")


async def _login(backend: AdminAuth, request: FakeRequest) -> bool:
    return await backend.login(cast(Request, request))


async def test_login_succeeds_for_active_staff_user(
    backend: AdminAuth,
    session_maker: async_sessionmaker[AsyncSession],
    session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(admin_module, "async_session_maker", session_maker)
    await create_user(session, username="boss", password=PASSWORD, is_staff=True)

    request = FakeRequest({"username": "boss", "password": PASSWORD})
    assert await _login(backend, request) is True
    assert request.session["admin_user"] == "boss"


async def test_login_rejects_missing_form_fields(backend: AdminAuth) -> None:
    assert await _login(backend, FakeRequest({})) is False


async def test_login_rejects_unknown_user(
    backend: AdminAuth,
    session_maker: async_sessionmaker[AsyncSession],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(admin_module, "async_session_maker", session_maker)
    request = FakeRequest({"username": "ghost", "password": PASSWORD})
    assert await _login(backend, request) is False


async def test_login_rejects_non_staff_user(
    backend: AdminAuth,
    session_maker: async_sessionmaker[AsyncSession],
    session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(admin_module, "async_session_maker", session_maker)
    await create_user(session, username="plain", password=PASSWORD, is_staff=False)

    request = FakeRequest({"username": "plain", "password": PASSWORD})
    assert await _login(backend, request) is False


async def test_login_rejects_wrong_password(
    backend: AdminAuth,
    session_maker: async_sessionmaker[AsyncSession],
    session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(admin_module, "async_session_maker", session_maker)
    await create_user(session, username="boss", password=PASSWORD, is_staff=True)

    request = FakeRequest({"username": "boss", "password": "wrong"})
    assert await _login(backend, request) is False


async def test_logout_clears_session(backend: AdminAuth) -> None:
    request = FakeRequest({}, session={"admin_user": "boss"})
    assert await backend.logout(cast(Request, request)) is True
    assert request.session == {}


async def test_authenticate_reflects_session(backend: AdminAuth) -> None:
    signed_in = FakeRequest({}, session={"admin_user": "boss"})
    anonymous = FakeRequest({})
    assert await backend.authenticate(cast(Request, signed_in)) is True
    assert await backend.authenticate(cast(Request, anonymous)) is False
