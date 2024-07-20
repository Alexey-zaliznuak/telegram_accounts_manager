from pydantic import PostgresDsn
from pydantic_settings import BaseSettings

from dotenv import load_dotenv


load_dotenv(".env", override=True)


class Settings(BaseSettings):
    TELEGRAM_API_ID: str
    TELEGRAM_API_HASH: str

    TELEGRAM_BOT_TOKEN: str

    DATABASE_URL: PostgresDsn


Settings = Settings()
