from httpx import AsyncClient
from redis.asyncio import Redis

from api.routes.time import CACHE_KEY, CACHE_TTL_SECONDS


async def test_current_time_is_computed_then_served_from_cache(
    client: AsyncClient, redis_client: Redis
) -> None:
    # First request: cache miss, so the time is computed and stored.
    first = await client.get("/api/time/")
    assert first.status_code == 200
    first_body = first.json()
    assert first_body["cached"] is False

    # Second request within the window: cache hit returns the same frozen time.
    second = await client.get("/api/time/")
    assert second.status_code == 200
    second_body = second.json()
    assert second_body["cached"] is True
    assert second_body["current_time"] == first_body["current_time"]


async def test_current_time_entry_expires_after_fifteen_minutes(
    client: AsyncClient, redis_client: Redis
) -> None:
    await client.get("/api/time/")

    ttl = await redis_client.ttl(CACHE_KEY)
    assert 0 < ttl <= CACHE_TTL_SECONDS
    assert CACHE_TTL_SECONDS == 15 * 60
