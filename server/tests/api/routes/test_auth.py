from datetime import UTC, datetime, timedelta

import jwt
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from tests.factories import create_user

DEMO_PASSWORD = "password-123"


def _make_token(**payload: object) -> str:
    now = datetime.now(UTC)
    return jwt.encode(
        {"iat": now, "exp": now + timedelta(minutes=5), **payload},
        settings.secret_key,
        algorithm="HS256",
    )


async def test_register_creates_a_user_who_can_then_log_in(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/register/", json={"username": "newbie", "password": "a-good-password"}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["access"] and body["refresh"]

    # The account was persisted (committed), so the new credentials authenticate.
    login = await client.post(
        "/api/token/", json={"username": "newbie", "password": "a-good-password"}
    )
    assert login.status_code == 200


async def test_register_rejects_a_taken_username(
    client: AsyncClient, session: AsyncSession
) -> None:
    await create_user(session, username="taken", password=DEMO_PASSWORD)

    response = await client.post(
        "/api/register/", json={"username": "taken", "password": "a-good-password"}
    )

    assert response.status_code == 400


async def test_register_rejects_a_too_short_password(client: AsyncClient) -> None:
    response = await client.post(
        "/api/register/", json={"username": "newbie", "password": "short"}
    )

    assert response.status_code == 422


async def test_obtain_token_returns_access_and_refresh(
    client: AsyncClient, session: AsyncSession
) -> None:
    await create_user(session, username="demo", password=DEMO_PASSWORD)

    response = await client.post(
        "/api/token/", json={"username": "demo", "password": DEMO_PASSWORD}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access"] and body["refresh"]


async def test_obtain_token_as_demo_logs_in_the_demo_user(
    client: AsyncClient, session: AsyncSession
) -> None:
    await create_user(session, username="demo", password=DEMO_PASSWORD)

    response = await client.post("/api/token/as-demo")

    assert response.status_code == 200
    body = response.json()
    assert body["access"] and body["refresh"]


async def test_obtain_token_rejects_wrong_password(
    client: AsyncClient, session: AsyncSession
) -> None:
    await create_user(session, username="demo", password=DEMO_PASSWORD)

    response = await client.post(
        "/api/token/", json={"username": "demo", "password": "wrong"}
    )

    assert response.status_code == 401


async def test_refresh_returns_a_new_access_token(
    client: AsyncClient, session: AsyncSession
) -> None:
    await create_user(session, username="demo", password=DEMO_PASSWORD)
    tokens = (
        await client.post(
            "/api/token/", json={"username": "demo", "password": DEMO_PASSWORD}
        )
    ).json()

    response = await client.post(
        "/api/token/refresh/", json={"refresh": tokens["refresh"]}
    )

    assert response.status_code == 200
    assert response.json()["access"]


async def test_refresh_rejects_a_garbage_token(client: AsyncClient) -> None:
    response = await client.post("/api/token/refresh/", json={"refresh": "not-a-jwt"})

    assert response.status_code == 401


async def test_refresh_rejects_an_access_token(client: AsyncClient) -> None:
    # A real, validly-signed token of the wrong type must be refused: this is the
    # token_type check in the production TokenIssuer, which the fake can't reach.
    access = _make_token(user_id=1, token_type="access")

    response = await client.post("/api/token/refresh/", json={"refresh": access})

    assert response.status_code == 401


async def test_refresh_rejects_a_non_integer_subject(client: AsyncClient) -> None:
    token = _make_token(user_id="not-an-int", token_type="refresh")

    response = await client.post("/api/token/refresh/", json={"refresh": token})

    assert response.status_code == 401


async def test_protected_endpoint_requires_a_token(client: AsyncClient) -> None:
    response = await client.get("/api/tasks/")

    assert response.status_code == 401


async def test_protected_endpoint_rejects_a_malformed_token(
    client: AsyncClient,
) -> None:
    response = await client.get(
        "/api/tasks/", headers={"Authorization": "Bearer nonsense"}
    )

    assert response.status_code == 401


async def test_protected_endpoint_rejects_a_non_integer_subject(
    client: AsyncClient,
) -> None:
    token = _make_token(user_id="nope", token_type="access")

    response = await client.get(
        "/api/tasks/", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401
