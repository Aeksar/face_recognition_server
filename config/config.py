from pydantic_settings import BaseSettings
import logging


EMBEDDING_EXPIRE = 2_592_000

class Settings(BaseSettings):
    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_DB: str
    MONGO_COLLECTION: str
    MONGO_USER: str
    MONGO_PASSWORD: str
    
    SECRET_KEY: bytes
    
    class Config:
        env_file = ".env"

logging.basicConfig(
    level=logging.INFO,
    format="[{asctime}] #{levelname} {filename} ({lineno}): {message}",
    style='{',
    encoding='UTF-8'
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)