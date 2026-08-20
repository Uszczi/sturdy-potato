from datetime import datetime

from pydantic import BaseModel


class CurrentTime(BaseModel):
    current_time: datetime
    # True when the value was served from the Redis cache rather than freshly
    # computed; makes the 15-minute caching observable to clients and tests.
    cached: bool
