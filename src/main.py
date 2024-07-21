import asyncio
import logging
import os
from logging.handlers import RotatingFileHandler

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from accounts.router import router as accounts_router
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

storage = MemoryStorage()

dp = Dispatcher(storage=storage)

dp.include_routers(accounts_router)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())
