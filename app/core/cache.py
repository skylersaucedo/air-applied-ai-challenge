import json
from typing import Any, Optional

import redis


class RedisCache:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis.get(key)
            if value is None:
                return None
            return json.loads(value)
        except Exception as e:
            print(f"Error getting from cache: {e}")
            return None

    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Set value in cache with expiration time in seconds"""
        try:
            serialized_value = json.dumps(value)
            return self.redis.setex(key, expire, serialized_value)
        except Exception as e:
            print(f"Error setting cache: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            print(f"Error deleting from cache: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return bool(self.redis.exists(key))
        except Exception as e:
            print(f"Error checking cache existence: {e}")
            return False 