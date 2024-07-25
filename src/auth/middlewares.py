from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Update
from aiogram.exceptions import Unauthorized
from aiogram.utils import executor

API_TOKEN = 'YOUR_BOT_API_TOKEN'
users_db = {}  # Простая имитация базы данных пользователей {telegram_id: system_id}

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


class AuthMiddleware(BaseMiddleware):
    async def on_process_update(self, update: Update, data: dict):
        if update.message:
            user_id = update.message.from_user.id
        elif update.callback_query:
            user_id = update.callback_query.from_user.id
        else:
            return

        if user_id not in users_db:
            if update.message and update.message.text not in ["/start", "/login"]:
                await update.message.reply("Access denied. Please use /login to log in.")
                raise Unauthorized()

            elif update.callback_query:
                await update.callback_query.message.answer("Access denied. Please use /login to log in.")
                raise Unauthorized()

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    if message.from_user.id in users_db:
        await message.reply("Добро пожаловать!")
    else:
        await message.reply("Welcome! Please use /login to log in.")

@dp.message_handler(commands=['login'])
async def cmd_login(message: types.Message):
    if message.from_user.id in users_db:
        await message.reply("You are already logged in!")
    else:
        await message.reply("Please enter your password:")
