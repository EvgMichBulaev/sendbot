import json
import os
from typing import List

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from pydantic_settings import BaseSettings, SettingsConfigDict


def _parse_admins(value: str) -> List[int]:
    """Parse ADMINS from comma-separated string or JSON array."""
    if not value or not value.strip():
        raise ValueError("ADMINS cannot be empty")
    value = value.strip()
    # Try JSON array first (e.g., "[123, 456]")
    if value.startswith("["):
        try:
            return [int(x) for x in json.loads(value)]
        except (json.JSONDecodeError, TypeError) as e:
            raise ValueError(f"Invalid JSON in ADMINS: {e}")
    # Fallback: comma-separated integers (e.g., "123, 456")
    try:
        result = [int(x.strip()) for x in value.split(",") if x.strip()]
        if not result:
            raise ValueError("ADMINS cannot be empty")
        return result
    except ValueError as e:
        if "invalid literal" in str(e):
            raise ValueError(f"Invalid integer in ADMINS: {e}")
        raise


class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMINS: str  # raw string, parsed via _parse_admins()
    FORMAT_LOG: str = "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}"
    LOG_ROTATION: str = "10 MB"
    DB_URL: str
    WEBHOOK_PATH: str
    WEBHOOK_URL: str
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "./.env")
    )

settings = Settings()

bot = Bot(token=settings.BOT_TOKEN,
          default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
admins = _parse_admins(settings.ADMINS)
database_url = settings.DB_URL
all_media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'configure')