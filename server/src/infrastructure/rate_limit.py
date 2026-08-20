"""A small in-process rate limiter for the authentication endpoints.

Login and refresh are unauthenticated and password-guessing targets, so they
get a per-client sliding-window cap. This keeps state in memory, which is enough
for a single process; behind several Uvicorn workers (or replicas) each process
counts independently, so the effective limit is multiplied by the worker count.
For strict global limits across workers, back this with a shared store (Redis).
"""

import time
from collections import defaultdict, deque
from collections.abc import Callable

from fastapi import Request

from use_cases.exceptions import TooManyRequests


class RateLimiter:
    """Sliding-window counter: at most ``max_requests`` per ``window_seconds``."""

    def __init__(
        self,
        *,
        max_requests: int,
        window_seconds: float,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._max = max_requests
        self._window = window_seconds
        self._clock = clock
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        """Record a hit for ``key`` and report whether it is within the limit."""
        now = self._clock()
        cutoff = now - self._window
        hits = self._hits[key]
        while hits and hits[0] <= cutoff:
            hits.popleft()
        if len(hits) >= self._max:
            return False
        hits.append(now)
        return True

    def reset(self) -> None:
        """Drop all recorded hits (used to isolate tests)."""
        self._hits.clear()


# Ten attempts per minute per client is generous for a human login yet closes
# the door on unthrottled online password guessing.
login_rate_limiter = RateLimiter(max_requests=10, window_seconds=60)


def _client_key(request: Request) -> str:
    return request.client.host if request.client is not None else "unknown"


def rate_limit_login(request: Request) -> None:
    """FastAPI dependency: throttle a client's auth attempts."""
    if not login_rate_limiter.allow(_client_key(request)):
        raise TooManyRequests()
