from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis, from_url

from config import settings

# A lazily-connecting client backed by a shared connection pool. Connections are
# only opened on first use, so importing this module never requires Redis to be
# reachable (mirrors how the SQLAlchemy engine in db.py connects lazily).
# ``decode_responses`` returns ``str`` values instead of ``bytes``.
redis_client: Redis = from_url(settings.redis_url, decode_responses=True)


async def get_redis() -> AsyncGenerator[Redis]:
    yield redis_client


RedisDep = Annotated[Redis, Depends(get_redis)]
