import os
from typing import List
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
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

settings = Settings()

bot = Bot(token=settings.BOT_TOKEN,
          default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
admins = settings.ADMINS
database_url = settings.DB_URL
all_media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'configure')