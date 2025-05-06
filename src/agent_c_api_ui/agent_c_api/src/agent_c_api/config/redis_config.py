from redis import asyncio as aioredis
from .env_config import settings

class RedisConfig:
    @staticmethod
    async def get_redis_client():
        return aioredis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            username=settings.REDIS_USERNAME,
            password=settings.REDIS_PASSWORD,
            encoding="utf8",
            decode_responses=True
        )

