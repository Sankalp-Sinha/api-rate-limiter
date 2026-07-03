import time
from dataclasses import dataclass
from threading import Lock
from typing import Dict, Tuple


@dataclass
class Bucket:
    tokens: float
    last_refill_time: float


class InMemoryTokenBucketLimiter:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buckets: Dict[str, Bucket] = {}
        self.lock = Lock()

    def allow_request(self, key: str, tokens_required: int = 1) -> Tuple[bool, int, int, int]:
        now = time.monotonic()

        with self.lock:
            bucket = self.buckets.get(key)

            if bucket is None:
                bucket = Bucket(
                    tokens=self.capacity,
                    last_refill_time=now
                )

            elapsed_time = now - bucket.last_refill_time
            tokens_to_add = elapsed_time * self.refill_rate

            bucket.tokens = min(self.capacity, bucket.tokens + tokens_to_add)
            bucket.last_refill_time = now

            if bucket.tokens >= tokens_required:
                bucket.tokens -= tokens_required
                allowed = True
            else:
                allowed = False

            self.buckets[key] = bucket

            remaining_tokens = int(bucket.tokens)

            if allowed:
                retry_after = 0
            else:
                missing_tokens = tokens_required - bucket.tokens
                retry_after = int(missing_tokens / self.refill_rate) + 1

            reset_after = int((self.capacity - bucket.tokens) / self.refill_rate)

            return allowed, remaining_tokens, retry_after, reset_after