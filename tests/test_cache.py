import json

import pytest
from fakeredis import FakeRedis

from app.core.cache import RedisCache


@pytest.fixture
def redis_cache():
    redis_client = FakeRedis()
    return RedisCache(redis_client)


@pytest.mark.asyncio
async def test_cache_set_get(redis_cache):
    key = "test_key"
    value = {"data": "test_value"}
    
    # Set value in cache
    await redis_cache.set(key, value, expire=60)
    
    # Get value from cache
    cached_value = await redis_cache.get(key)
    assert cached_value == value


@pytest.mark.asyncio
async def test_cache_miss(redis_cache):
    key = "nonexistent_key"
    cached_value = await redis_cache.get(key)
    assert cached_value is None


@pytest.mark.asyncio
async def test_cache_delete(redis_cache):
    key = "test_key"
    value = {"data": "test_value"}
    
    # Set and verify value
    await redis_cache.set(key, value)
    assert await redis_cache.get(key) == value
    
    # Delete and verify removal
    await redis_cache.delete(key)
    assert await redis_cache.get(key) is None


@pytest.mark.asyncio
async def test_cache_complex_data(redis_cache):
    key = "complex_key"
    value = {
        "string": "test",
        "number": 42,
        "list": [1, 2, 3],
        "nested": {"key": "value"}
    }
    
    await redis_cache.set(key, value)
    cached_value = await redis_cache.get(key)
    assert cached_value == value


@pytest.mark.asyncio
async def test_cache_multiple_keys(redis_cache):
    test_data = {
        "key1": {"data": "value1"},
        "key2": {"data": "value2"},
        "key3": {"data": "value3"}
    }
    
    # Set multiple values
    for key, value in test_data.items():
        await redis_cache.set(key, value)
    
    # Verify all values
    for key, value in test_data.items():
        assert await redis_cache.get(key) == value 