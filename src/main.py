import asyncio
import logging
import os
from logging.handlers import RotatingFileHandler

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis import Redis

from accounts_management.router import router as accounts_management_router
from settings import Settings


os.makedirs("./logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(name)s %(levelname)s [%(asctime)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler('./logs/bot.log', maxBytes=10_000 * 100, backupCount=1),  # save about 10_000 log entries
    ]
)


bot = Bot(
    token=Settings.TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)

storage = RedisStorage(Redis.from_url(str(Settings.REDIS_URL)))

dp = Dispatcher(storage=storage)

dp.include_routers(accounts_management_router)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(Settings.DEFAULT_BOT_COMMANDS)
    await dp.start_polling(bot)


asyncio.run(main())
