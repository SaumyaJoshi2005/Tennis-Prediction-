"""
cache.py — Redis prediction cache
==================================
BUGS FIXED
----------
1. Redis host hardcoded to 'localhost' — inside Docker the Redis service
   is reachable via its compose service name 'redis', not localhost.
   Fixed: reads REDIS_HOST from environment variable (default 'redis').

2. No error handling — if Redis is unavailable, every prediction request
   raised an unhandled ConnectionError and crashed the API.
   Fixed: cache miss (None) returned on any Redis error so the API
   gracefully falls back to running the model.
"""

import os
import json
import logging
import redis

logger = logging.getLogger(__name__)

# FIX 1: Read host from env so it works both locally and inside Docker.
# Locally:  REDIS_HOST defaults to 'localhost'
# Docker:   docker-compose sets REDIS_HOST=redis (the service name)
_redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True,
    socket_connect_timeout=2,   # fail fast if Redis is unreachable
)


def get_cached_prediction(key: str):
    """
    Return cached prediction dict, or None on cache miss / Redis error.
    Never raises — cache failure should never break the prediction path.
    """
    # FIX 2: Wrap in try/except so a Redis outage returns None (cache miss)
    # instead of propagating a ConnectionError to the API caller.
    try:
        value = _redis_client.get(key)
        if value:
            return json.loads(value)
    except Exception as e:
        logger.warning("Redis GET failed (key=%s): %s", key, e)
    return None


def set_cached_prediction(key: str, value: dict, ttl: int = 3600):
    """
    Cache a prediction result. Silently skips on Redis error.
    TTL defaults to 1 hour — predictions for the same matchup won't change
    within a session, so caching is safe here.
    """
    try:
        _redis_client.setex(key, ttl, json.dumps(value))
    except Exception as e:
        logger.warning("Redis SET failed (key=%s): %s", key, e)
