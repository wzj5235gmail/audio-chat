from redis import asyncio as aioredis
import os

redis_url = os.getenv("REDIS_URL")

redis = aioredis.from_url(redis_url)