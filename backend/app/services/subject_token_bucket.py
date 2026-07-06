import math
import time
from dataclasses import dataclass

from app.services.redis_client import (
    redis_client,
)


TOKEN_BUCKET_LUA = """
local key = KEYS[1]

local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local tokens_required = tonumber(ARGV[4])
local ttl_seconds = tonumber(ARGV[5])

local values = redis.call(
    "HMGET",
    key,
    "tokens",
    "last_refill_time"
)

local tokens = tonumber(values[1])
local last_refill_time = tonumber(values[2])

if tokens == nil then
    tokens = capacity
end

if last_refill_time == nil then
    last_refill_time = now
end

local elapsed = now - last_refill_time

if elapsed < 0 then
    elapsed = 0
end

tokens = math.min(
    capacity,
    tokens + (elapsed * refill_rate)
)

local allowed = 0
local retry_after = 0

if tokens >= tokens_required then
    allowed = 1
    tokens = tokens - tokens_required
else
    local missing_tokens = (
        tokens_required - tokens
    )

    retry_after = math.ceil(
        missing_tokens / refill_rate
    )
end

redis.call(
    "HSET",
    key,
    "tokens",
    tokens,
    "last_refill_time",
    now
)

redis.call(
    "EXPIRE",
    key,
    ttl_seconds
)

local remaining = math.floor(tokens)

local reset_after = math.ceil(
    (capacity - tokens) / refill_rate
)

return {
    allowed,
    remaining,
    retry_after,
    reset_after
}
"""


@dataclass
class SubjectBucketDecision:
    allowed: bool
    remaining: int
    retry_after_seconds: int
    reset_after_seconds: int


async def consume_subject_bucket(
    redis_key: str,
    capacity: int,
    refill_rate: float,
    tokens_required: int,
) -> SubjectBucketDecision:
    now = time.time()

    # Once enough idle time has passed to fully
    # refill the bucket, old Redis state is no
    # longer useful.
    ttl_seconds = max(
        60,
        math.ceil(
            capacity / refill_rate
        ) + 60,
    )

    result = await redis_client.eval(
        TOKEN_BUCKET_LUA,
        1,
        redis_key,
        capacity,
        refill_rate,
        now,
        tokens_required,
        ttl_seconds,
    )

    return SubjectBucketDecision(
        allowed=bool(int(result[0])),
        remaining=int(result[1]),
        retry_after_seconds=int(
            result[2]
        ),
        reset_after_seconds=int(
            result[3]
        ),
    )