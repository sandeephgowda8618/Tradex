from __future__ import annotations

import json
from typing import Any, Optional


class RedisCache:
    def __init__(self, client: Any) -> None:
        self.client = client

    def get_json(self, key: str) -> Optional[Any]:
        if self.client is None:
            return None
        value = self.client.get(key)
        if value is None:
            return None
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None

    def set_json(self, key: str, value: Any, ttl_seconds: int) -> None:
        if self.client is None:
            return
        payload = json.dumps(value, separators=(",", ":"), ensure_ascii=True)
        self.client.setex(key, ttl_seconds, payload)
