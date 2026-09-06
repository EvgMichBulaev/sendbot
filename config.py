import os
from typing import List, Union

import json
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMINS: List[int]
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

    @field_validator("ADMINS", mode="before")
    @classmethod
    def parse_admins(cls, value: Union[str, List[int]]) -> List[int]:
        """Parse ADMINS from comma-separated string or JSON array."""
        if isinstance(value, list):
            return value
        if not value or not value.strip():
            raise ValueError("ADMINS cannot be empty")
        # Try JSON array first (e.g., "[123, 456]")
        value = value.strip()
        if value.startswith("["):
            try:
                return json.loads(value)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in ADMINS: {e}")
        # Fallback: comma-separated integers (e.g., "123, 456")
        try:
            return [int(x.strip()) for x in value.split(",") if x.strip()]
        except ValueError as e:
            raise ValueError(f"Invalid integer in ADMINS: {e}")

settings = Settings()

bot = Bot(token=settings.BOT_TOKEN,
          default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
admins = settings.ADMINS
database_url = settings.DB_URL
all_media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'configure')