"""
Redis-backed cache for model predictions.

Allows the FastAPI to serve model predictions with sub-millisecond latency
when the same input was seen before: the result is stored in Redis keyed by
(model name, input hash) with a configurable TTL.

Degrades gracefully to a no-op when Redis is unavailable.
"""
import hashlib
import json
import os
import time
from typing import Any, Callable, Optional

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DEFAULT_TTL = int(os.getenv("MODEL_CACHE_TTL", "3600"))
_PREFIX = "rasd:model:"

_client = None


def _get_client():
    global _client
    if _client is None:
        try:
            import redis as _redis
            _client = _redis.from_url(REDIS_URL, decode_responses=True)
            _client.ping()
        except Exception:
            _client = False
    return _client or None


def _b64(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def cache_key(model_name: str, payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, default=str)
    return f"{_PREFIX}{model_name}:{_b64(raw)}"


def get(model_name: str, payload: Any) -> Optional[Any]:
    client = _get_client()
    if client is None:
        return None
    try:
        hit = client.get(cache_key(model_name, payload))
        if hit is None:
            return None
        return json.loads(hit)
    except Exception:
        return None


def put(model_name: str, payload: Any, result: Any, ttl: Optional[int] = None) -> None:
    client = _get_client()
    if client is None:
        return
    try:
        client.setex(cache_key(model_name, payload), ttl or DEFAULT_TTL, json.dumps(result, default=str))
    except Exception:
        pass


def cached_predict(model_name: str, ttl: Optional[int] = None) -> Callable:
    """Decorator: runs the wrapped predict function unless the result is cached.

    The wrapped function must accept a single JSON-serializable argument
    (the request payload). Example:

        @cached_predict("spam-classifier")
        def _predict(payload):
            ...
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(payload: Any) -> Any:
            hit = get(model_name, payload)
            if hit is not None:
                if isinstance(hit, dict):
                    hit = dict(hit)
                    hit["_cache"] = {"hit": True, "inference_ms": 0}
                return hit
            start = time.time()
            result = func(payload)
            elapsed = round((time.time() - start) * 1000, 2)
            if isinstance(result, dict):
                result = dict(result)
                result["_cache"] = {"hit": False, "inference_ms": elapsed}
            put(model_name, payload, result, ttl)
            return result
        return wrapper
    return decorator


def invalidate(model_name: Optional[str] = None) -> int:
    """Delete all cached predictions, optionally for one model. Returns count."""
    client = _get_client()
    if client is None:
        return 0
    try:
        if model_name:
            pattern = f"{_PREFIX}{model_name}:*"
        else:
            pattern = f"{_PREFIX}*"
        keys = list(client.scan_iter(match=pattern))
        if keys:
            client.delete(*keys)
        return len(keys)
    except Exception:
        return 0
