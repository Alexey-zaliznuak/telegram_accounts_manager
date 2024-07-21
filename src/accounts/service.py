import logging
from typing import NamedTuple

from aiogram.types import Message
from telethon import TelegramClient
from telethon.sessions import StringSession, Session

from core import TelegramService
from core.database.orm_service import BaseORMService
from core.types import FailureList, SuccessList
from core.utils import HTMLFormatter
from settings import Settings
from database import get_async_session_with_context_manager as get_async_session

from .models import TelegramAccount


logger = logging.getLogger(__name__)


class PhoneCodePair(NamedTuple):
    phone: str
    code: str


class _TelegramAccountsOrmService(BaseORMService):
    BASE_MODEL = TelegramAccount


class TelegramAccountsService(TelegramService, ):
    objects = _TelegramAccountsOrmService

    async def save_account(self, credentials: PhoneCodePair):
        """
        Create new client, sign in and create new Telegram Account with session
        """
        client = await self.create_new_client_and_connect()
        client.sign_in(phone=credentials.phone, code=credentials.code)

        async with get_async_session() as db_session:
            try:
                new_account = TelegramAccount(
                    phone=credentials.phone,
                    session=client.session.save()
                )

                await self.objects.save_and_refresh(new_account, db_session)

                if not new_account:
                    raise Exception("Failed to create Telegram Account")

            finally:
                await client.disconnect()

        return new_account

    @staticmethod
    def build_send_code_result_message(result: tuple[SuccessList[str], FailureList[str]]):
        success, failure = result

        success_message_part = (
            "Коды успешно отправлены на:"
            + "\n\n"
            + "\n".join([HTMLFormatter.code(phone) for phone in success]) + "\n"
        ) if success else ""

        failure_message_part = (
            "Ошибка при попытке отправить код на:"
            + "\n\n"
            + "\n".join([HTMLFormatter.code(phone) for phone in failure]) + "\n"
        ) if failure else ""

        return (
            + success_message_part
            + "\n"
            + failure_message_part
        )

    @staticmethod
    async def parse_phone_code_pairs_and_answer_if_errors(message: Message) -> list[PhoneCodePair]:
        # TODO split into 2 methods
        """
        Return parsed phone code pairs by format
        <phone> <code>

        If got errors, message about it.
        """
        data = list(set(message.text.splitlines()))

        result = []

        for pair in data:
            try:
                pair = pair.split()
                result.append(PhoneCodePair(phone=pair[0], code=pair[1]))

            except:
                msg = f"Ошибка при сканировании пары: {pair}"

                logger.error(msg)
                await message.answer(msg)

        return result

    @staticmethod
    async def build_sign_in_accounts_result_message(
        success: list[str],
        failure: list[str],
        remaining: list[str],
    ):
        success_message_part = (
            "Выполнен успешный вход:" + "\n"
            + "\n".join(success)
        ) if success else ""

        failure_message_part = (
            "Возникла ошибка:" + "\n"
            + "\n".join(failure)
        ) if failure else ""

        remaining_message_part = (
            "Не был указан код / возникла ошибка при входе:" + "\n"
            + "\n".join(remaining)
            + "\n"
            + HTMLFormatter.bold(
                "Вы можете заново отправить коды к оставшимся номерам "
                "или отправить команду для их пропуска"
                "(номера с успешным входом будут сохранены)"
            )
        ) if remaining else ""

        return (
            success_message_part,
            failure_message_part,
            remaining_message_part,
        )
