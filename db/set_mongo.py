import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from config.config import Settings, logger

cfg = Settings()

async def connect_to_mongodb():
    try:
        client = AsyncIOMotorClient(
            f"mongodb://{cfg.MONGO_USER}:{cfg.MONGO_PASSWORD}@{cfg.MONGO_HOST}:{cfg.MONGO_PORT}/"
        )
        db = client[cfg.MONGO_DB]
        logger.info("Succeful connect to MongoDB!")
        return db
    except Exception as e:
        logger.info(f"Unsucceful connect to MongoDB: {e}")
        return None