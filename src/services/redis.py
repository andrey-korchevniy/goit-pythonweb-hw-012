"""
Module for working with Redis for data caching.

This module provides functions for connecting to Redis and performing
caching operations for users and other data.
"""

import json
from typing import Optional

import redis
from fastapi import Depends

from src.conf.config import settings
from src.schemas import UserResponse

# Creating global Redis connection
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)

async def get_redis_client():
    """
    Function to get Redis client.
    
    Returns:
        Redis client.
    """
    return redis_client

async def cache_user(user: UserResponse) -> None:
    """
    Caching user in Redis.
    
    Args:
        user: User to cache.
    """
    user_data = user.model_dump()
    key = f"user:{user.username}"
    redis_client.setex(
        key, 
        settings.REDIS_USER_TTL, 
        json.dumps(user_data)
    )

async def get_cached_user(username: str) -> Optional[dict]:
    """
    Get cached user data.
    
    Args:
        username: Username.
        
    Returns:
        User data from cache or None if user is not found in cache.
    """
    key = f"user:{username}"
    cached_user = redis_client.get(key)
    
    if cached_user:
        return json.loads(cached_user)
    
    return None

async def invalidate_user_cache(username: str) -> None:
    """
    Invalidate user cache.
    
    Args:
        username: Username.
    """
    key = f"user:{username}"
    redis_client.delete(key) 