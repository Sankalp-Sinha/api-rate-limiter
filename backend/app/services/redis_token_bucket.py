import time
from typing import Tuple

from redis.asyncio import Redis


TOKEN_BUCKET_LUA_SCRIPT = """
local key = KEYS[1]

local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local tokens_required = tonumber(ARGV[3])
local now = tonumber(ARGV[4])
local ttl_seconds = tonumber(ARGV[5])

local bucket = redis.call("HMGET", key, "tokens", "last_refill_time")

local tokens = tonumber(bucket[1])
local last_refill_time = tonumber(bucket[2])

if tokens == nil then
    tokens = capacity
end

if last_refill_time == nil then
    last_refill_time = now
end

local elapsed_time = math.max(0, now - last_refill_time)
local tokens_to_add = elapsed_time * refill_rate

tokens = math.min(capacity, tokens + tokens_to_add)
last_refill_time = now

local allowed = 0

if tokens >= tokens_required then
    tokens = tokens - tokens_required
    allowed = 1
end

redis.call("HSET", key, "tokens", tokens, "last_refill_time", last_refill_time)
redis.call("EXPIRE", key, ttl_seconds)

local remaining_tokens = math.floor(tokens)

local retry_after = 0

if allowed == 0 then
    local missing_tokens = tokens_required - tokens
    retry_after = math.ceil(missing_tokens / refill_rate)
end

local reset_after = math.ceil((capacity - tokens) / refill_rate)

return {
    allowed,
    remaining_tokens,
    retry_after,
    reset_after
}
"""


class RedisTokenBucketLimiter:
    def __init__(self, redis_client: Redis, capacity: int, refill_rate: float):
        self.redis_client = redis_client
        self.capacity = capacity
        self.refill_rate = refill_rate

    async def allow_request(self, key: str, tokens_required: int = 1) -> Tuple[bool, int, int, int]:
        redis_key = f"rate_limit:{key}"

        now = time.time()
        ttl_seconds = int((self.capacity / self.refill_rate) * 2) + 60

        result = await self.redis_client.eval(
            TOKEN_BUCKET_LUA_SCRIPT,
            1,
            redis_key,
            self.capacity,
            self.refill_rate,
            tokens_required,
            now,
            ttl_seconds
        )

        allowed = bool(int(result[0]))
        remaining_tokens = int(result[1])
        retry_after = int(result[2])
        reset_after = int(result[3])

        return allowed, remaining_tokens, retry_after, reset_after