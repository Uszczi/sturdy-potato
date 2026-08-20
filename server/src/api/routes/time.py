from datetime import UTC, datetime

from fastapi import APIRouter

from infrastructure.cache import RedisDep
from schemas.time import CurrentTime

router = APIRouter(prefix="/time", tags=["api"])

# The current-time payload is cached in Redis for 15 minutes to demonstrate
# read-through caching: the first request computes and stores the timestamp, and
# every request within the window gets that same cached value back (so the time
# visibly "freezes" until the entry expires).
CACHE_KEY = "current_time"
CACHE_TTL_SECONDS = 15 * 60


@router.get("/", operation_id="api_time_read")
async def read_current_time(redis: RedisDep) -> CurrentTime:
    cached = await redis.get(CACHE_KEY)
    if cached is not None:
        # The client is created with decode_responses=True, so values come back
        # as str; assert it to narrow the broad redis-py return type for mypy.
        assert isinstance(cached, str)
        return CurrentTime(current_time=datetime.fromisoformat(cached), cached=True)

    now = datetime.now(UTC)
    await redis.set(CACHE_KEY, now.isoformat(), ex=CACHE_TTL_SECONDS)
    return CurrentTime(current_time=now, cached=False)
