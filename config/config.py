from pydantic_settings import BaseSettings
import logging

class Settings(BaseSettings):
    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_DB: str
    MONGO_COLLECTION: str
    MONGO_USER: str
    MONGO_PASSWORD: str
    

logging.basicConfig(
    level=logging.ERROR,
    format="[{asctime}] #{levelname} {filename} ({lineno}): {message}",
    style='{',
    encoding='UTF-8'
)

formatter = logging.Formatter("[{asctime}] #{levelname} {filename} ({lineno}): {message}", style='{',)

logger = logging.getLogger(__name__)