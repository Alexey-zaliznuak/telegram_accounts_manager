import asyncio
import logging
from functools import wraps

from telethon import TelegramClient
from telethon.errors import FloodError
from telethon.sessions import Session, StringSession
from telethon.tl.functions.auth import SendCodeRequest
from telethon.types import CodeSettings

from core.types import FailureList, SuccessList
from core.utils import args_to_list, time_to_seconds
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


class TelegramService:
    SEND_REQUEST_CODE_INTERVAL = time_to_seconds(seconds=3)

    async def request_code(self, client: TelegramClient, *phones: str | list[str]) -> tuple[SuccessList[str], FailureList[str]]:
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

        await self.connect_if_needs(client)

        for index, phone in enumerate(phones):
            try:
                await self.__request_code_single(phone, settings, client)

                # Sleep only if this is not the last iteration
                if index < len(phones) - 1:
                    await asyncio.sleep(self.SEND_REQUEST_CODE_INTERVAL)

                success.append(phone)

            except FloodError as e:
                logger.error(f"Failed to get code for phone: {phone}" + str(e))

                failure.append(phone)

        return success, failure

    def create_new_client(self, session: Session = None) -> TelegramClient:
        session = session if session else StringSession()

        return TelegramClient(session, Settings.TELEGRAM_API_ID, Settings.TELEGRAM_API_HASH)

    async def create_new_client_and_connect(self, session: Session = None) -> TelegramClient:
        client = self.create_new_client()
        await client.connect()

        return client

    @retry_on_flood(retries=5)
    async def __request_code_single(self, phone: str, settings: CodeSettings, client: TelegramClient):
        await client(
            SendCodeRequest(
                phone_number=phone,
                api_id=client.api_id,
                api_hash=client.api_hash,
                settings=CodeSettings(),  # TODO use from params
            )
        )

    async def connect_if_needs(self, client: TelegramClient):
        if not client.is_connected():
            await client.connect()
