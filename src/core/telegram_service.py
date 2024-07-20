import asyncio
import logging
from functools import wraps

from telethon import TelegramClient
from telethon.errors import FloodError
from telethon.sessions import StringSession
from telethon.tl.functions.auth import SendCodeRequest
from telethon.types import CodeSettings

from core.types import FailureList, SuccessList
from core.utils import SingletonMeta, args_to_list, time_to_seconds
from settings import Settings


logger = logging.getLogger(__name__)


def retry_on_flood(retries=10):
    """
    Retry function if got FloodError
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0

            while attempt != retries:
                try:
                    attempt += 1
                    return await func(*args, **kwargs)

                except FloodError as e:
                    logger.error(f"Rate limit exceeded. Waiting {e.seconds} seconds. Attempt {attempt + 1} of {retries}.")

                    await asyncio.sleep(e.seconds)

            raise FloodError(e.seconds)
        return wrapper
    return decorator


class TelegramService(metaclass=SingletonMeta):
    client = TelegramClient(StringSession(), Settings.TELEGRAM_API_ID, Settings.TELEGRAM_API_HASH)

    SEND_REQUEST_CODE_INTERVAL = time_to_seconds(seconds=3)


    async def request_code(self, *phones: str | list[str]) -> tuple[SuccessList[str], FailureList[str]]:
        """
        Send code request to telegram app.
        """

        phones = args_to_list(*phones)

        success = []
        failure = []

        settings = CodeSettings(
            allow_flashcall=False,   # Не разрешать флэш-вызов
            current_number=True,     # Использовать текущий номер
            allow_app_hash=True,     # Разрешить использование app hash
            allow_missed_call=False, # Не разрешать использование звонка
            allow_firebase=False,    # Не разрешать использование Firebase
            unknown_number=False,    # Номер не является неизвестным
            app_sandbox=False        # Не использовать песочницу приложения
        )

        for index, phone in enumerate(phones):
            try:
                await self.__request_code_single(phone, settings)

                # Sleep only if this is not the last iteration
                if index < len(phones) - 1:
                    await asyncio.sleep(self.SEND_REQUEST_CODE_INTERVAL)

                success.append(phone)

            except FloodError as e:
                logger.error(f"Failed to get code for phone: {phone}")

                failure.append(phone)

        return success, failure


    @retry_on_flood(retries=5)
    async def __request_code_single(self, phone: str, settings: CodeSettings):
        await self.connect_if_needs()

        await self.client(
            SendCodeRequest(
                phone_number=phone,
                api_id=self.client.api_id,
                api_hash=self.client.api_hash,
                settings=CodeSettings(),
            )
        )


    async def connect_if_needs(self):
        if not self.client.is_connected():
            await self.client.connect()
