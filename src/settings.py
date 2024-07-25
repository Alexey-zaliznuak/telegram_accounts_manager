from aiogram.types import BotCommand

from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings

from dotenv import load_dotenv


load_dotenv(".env", override=True)


class Settings(BaseSettings):
    DEFAULT_BOT_COMMANDS = [
        BotCommand(command="/import", desctiption="Загрузить аккаунты"),
        BotCommand(command="/get_accounts", desctiption="Получить аккаунты"),
    ]

    TELEGRAM_API_ID: str
    TELEGRAM_API_HASH: str

    TELEGRAM_BOT_TOKEN: str

    DATABASE_URL: PostgresDsn
    REDIS_URL: RedisDsn


Settings = Settings()
