import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from config.config import Settings, logger

cfg = Settings()

def connect_to_mongodb():
    try:
        client = AsyncIOMotorClient(
            f"mongodb://{cfg.MONGO_USER}:{cfg.MONGO_PASSWORD}@{cfg.MONGO_HOST}:{cfg.MONGO_PORT}/"
        )
        logger.info("Успешное подключение к монго")
        return client
    except Exception as e:
        logger.info(f"Ошибка подключения к монго: {e}")
        return None