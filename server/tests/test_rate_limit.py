import pytest
from httpx import AsyncClient
from starlette.requests import Request

from infrastructure.rate_limit import RateLimiter, rate_limit_login
from use_cases.exceptions import TooManyRequests


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def test_allows_up_to_the_limit_then_blocks() -> None:
    limiter = RateLimiter(max_requests=2, window_seconds=60, clock=FakeClock())

    assert limiter.allow("ip") is True
    assert limiter.allow("ip") is True
    assert limiter.allow("ip") is False


def test_window_slides_so_old_hits_expire() -> None:
    clock = FakeClock()
    limiter = RateLimiter(max_requests=1, window_seconds=10, clock=clock)

    assert limiter.allow("ip") is True
    assert limiter.allow("ip") is False

    clock.now = 11  # past the window: the earlier hit no longer counts
    assert limiter.allow("ip") is True


def test_keys_are_independent() -> None:
    limiter = RateLimiter(max_requests=1, window_seconds=60, clock=FakeClock())

    assert limiter.allow("a") is True
    assert limiter.allow("b") is True


def test_reset_clears_recorded_hits() -> None:
    limiter = RateLimiter(max_requests=1, window_seconds=60, clock=FakeClock())

    assert limiter.allow("ip") is True
    limiter.reset()
    assert limiter.allow("ip") is True


def test_dependency_falls_back_to_unknown_when_no_client() -> None:
    # A scope with no "client" leaves request.client None; the limiter still
    # keys the request (as "unknown") instead of crashing.
    request = Request({"type": "http", "headers": []})
    rate_limit_login(request)  # first call is allowed, so it must not raise


async def test_login_endpoint_is_rate_limited(client: AsyncClient) -> None:
    payload = {"username": "demo", "password": "whatever"}

    # The limiter allows 10 attempts per client per minute; the 11th is refused
    # before the credentials are even checked.
    for _ in range(10):
        response = await client.post("/api/token/", json=payload)
        assert response.status_code == 401

    blocked = await client.post("/api/token/", json=payload)
    assert blocked.status_code == 429
    assert blocked.headers["Retry-After"] == TooManyRequests.headers["Retry-After"]


def test_too_many_requests_carries_a_retry_after_header() -> None:
    assert TooManyRequests().headers == {"Retry-After": "60"}


@pytest.mark.parametrize("attempts", [1, 5])
def test_limiter_records_each_attempt(attempts: int) -> None:
    limiter = RateLimiter(max_requests=10, window_seconds=60, clock=FakeClock())
    for _ in range(attempts):
        assert limiter.allow("ip") is True
