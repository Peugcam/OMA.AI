"""
Advanced Rate Limiting with Redis
Implements token bucket and sliding window algorithms
"""

import time
from typing import Optional
from redis import Redis
from functools import wraps
import hashlib

class RateLimiter:
    """Token bucket rate limiter with Redis backend"""

    def __init__(self, redis_client: Redis, prefix: str = "oma:ratelimit"):
        self.redis = redis_client
        self.prefix = prefix

    def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple[bool, dict]:
        """
        Check if request is within rate limit

        Returns:
            (allowed: bool, info: dict)
        """
        redis_key = f"{self.prefix}:{key}"
        current_time = int(time.time())
        window_start = current_time - window_seconds

        pipe = self.redis.pipeline()

        # Remove old entries
        pipe.zremrangebyscore(redis_key, 0, window_start)

        # Count current requests
        pipe.zcard(redis_key)

        # Add current request
        pipe.zadd(redis_key, {str(current_time): current_time})

        # Set expiration
        pipe.expire(redis_key, window_seconds)

        results = pipe.execute()
        current_requests = results[1]

        allowed = current_requests < max_requests

        info = {
            "allowed": allowed,
            "current_requests": current_requests,
            "max_requests": max_requests,
            "reset_at": current_time + window_seconds,
            "retry_after": window_seconds if not allowed else 0
        }

        return allowed, info

    def decorator(self, max_requests: int, window_seconds: int):
        """Decorator for rate limiting functions"""
        def decorator_wrapper(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Extract identifier (IP, user_id, etc.)
                identifier = kwargs.get('identifier') or args[0] if args else 'anonymous'
                key = f"{func.__name__}:{identifier}"

                allowed, info = self.check_rate_limit(key, max_requests, window_seconds)

                if not allowed:
                    from fastapi import HTTPException
                    raise HTTPException(
                        status_code=429,
                        detail=f"Rate limit exceeded. Retry after {info['retry_after']}s",
                        headers={"Retry-After": str(info['retry_after'])}
                    )

                return await func(*args, **kwargs)

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                identifier = kwargs.get('identifier') or args[0] if args else 'anonymous'
                key = f"{func.__name__}:{identifier}"

                allowed, info = self.check_rate_limit(key, max_requests, window_seconds)

                if not allowed:
                    raise Exception(f"Rate limit exceeded. Retry after {info['retry_after']}s")

                return func(*args, **kwargs)

            # Return appropriate wrapper based on function type
            import inspect
            if inspect.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper

        return decorator_wrapper


class CostTracker:
    """Track API costs in real-time"""

    def __init__(self, redis_client: Redis):
        self.redis = redis_client

        # Cost per 1M tokens
        self.costs = {
            "openrouter:qwen-2.5-7b": 0.09,
            "openrouter:phi-3.5": 0.10,
            "openrouter:gemma-2-9b": 0.20,
            "pexels": 0.0,  # Free
            "stability-ai": 0.04  # Per image
        }

    def track_request(self, service: str, tokens: int = 0, items: int = 1):
        """Track API request cost"""
        cost_key = f"oma:cost:daily:{time.strftime('%Y%m%d')}"
        service_key = f"{cost_key}:{service}"

        cost_per_unit = self.costs.get(service, 0)

        if "openrouter" in service:
            # Token-based pricing
            cost = (tokens / 1_000_000) * cost_per_unit
        else:
            # Item-based pricing
            cost = items * cost_per_unit

        pipe = self.redis.pipeline()
        pipe.incrbyfloat(cost_key, cost)
        pipe.incrbyfloat(service_key, cost)
        pipe.expire(cost_key, 86400 * 7)  # Keep 7 days
        pipe.execute()

        return cost

    def get_daily_cost(self, date: Optional[str] = None) -> dict:
        """Get cost breakdown for a day"""
        if date is None:
            date = time.strftime('%Y%m%d')

        cost_key = f"oma:cost:daily:{date}"
        total = float(self.redis.get(cost_key) or 0)

        # Get breakdown
        breakdown = {}
        for service in self.costs.keys():
            service_key = f"{cost_key}:{service}"
            cost = float(self.redis.get(service_key) or 0)
            if cost > 0:
                breakdown[service] = round(cost, 4)

        return {
            "date": date,
            "total": round(total, 4),
            "breakdown": breakdown
        }


class CacheManager:
    """Intelligent caching with Redis"""

    def __init__(self, redis_client: Redis, default_ttl: int = 3600):
        self.redis = redis_client
        self.default_ttl = default_ttl

    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_parts = [prefix] + [str(arg) for arg in args]
        if kwargs:
            key_parts.append(hashlib.md5(str(sorted(kwargs.items())).encode()).hexdigest())
        return ":".join(key_parts)

    def get(self, key: str):
        """Get cached value"""
        import json
        value = self.redis.get(f"oma:cache:{key}")
        return json.loads(value) if value else None

    def set(self, key: str, value, ttl: Optional[int] = None):
        """Set cached value"""
        import json
        self.redis.setex(
            f"oma:cache:{key}",
            ttl or self.default_ttl,
            json.dumps(value)
        )

    def cache_decorator(self, ttl: int = None, prefix: str = "func"):
        """Decorator for caching function results"""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                cache_key = self._make_key(prefix, func.__name__, *args, **kwargs)

                # Try cache first
                cached = self.get(cache_key)
                if cached is not None:
                    return cached

                # Execute function
                result = await func(*args, **kwargs)

                # Cache result
                self.set(cache_key, result, ttl)

                return result

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                cache_key = self._make_key(prefix, func.__name__, *args, **kwargs)

                cached = self.get(cache_key)
                if cached is not None:
                    return cached

                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl)

                return result

            import inspect
            if inspect.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper

        return decorator
