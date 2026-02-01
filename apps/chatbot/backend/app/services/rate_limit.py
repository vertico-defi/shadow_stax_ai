from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
from typing import Dict, List


@dataclass
class RateLimitState:
    timestamps: List[datetime]


class SlidingWindowRateLimiter:
    def __init__(self, max_per_minute: int, burst: int) -> None:
        self._max_per_minute = max_per_minute
        self._burst = burst
        self._state: Dict[str, RateLimitState] = {}
        self._lock = asyncio.Lock()

    async def allow(self, key: str) -> bool:
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=1)
        async with self._lock:
            state = self._state.get(key)
            if state is None:
                state = RateLimitState(timestamps=[])
                self._state[key] = state

            state.timestamps = [ts for ts in state.timestamps if ts >= window_start]
            limit = self._max_per_minute + self._burst
            if len(state.timestamps) >= limit:
                return False
            state.timestamps.append(now)
            return True
