from redis import asyncio as aioredis
import os

if os.environ.get("ENV") == "production":
    redis_url = os.environ.get("REDIS_URL_DOCKER")
else:
    redis_url = os.environ.get("REDIS_URL_LOCAL")

redis = aioredis.from_url(redis_url)
