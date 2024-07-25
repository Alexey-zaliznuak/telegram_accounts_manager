import logging

from aiogram.types import Message
from telethon import TelegramClient
from telethon.sessions import StringSession, Session
from telethon.errors import PhoneCodeExpiredError
from sqlalchemy import delete, func, select, and_, true
from sqlalchemy.ext.asyncio import AsyncSession

from core.telegram_service import (
    TelegramService,
)
from core.database.orm_service import BaseORMService
from core.types import PhoneCode, failure_message, is_success
from core.utils import HTMLFormatter
from database import get_async_session_with_context_manager as get_async_session

from .models import TelegramAccount


logger = logging.getLogger(__name__)


class _TelegramAccountsOrmService(BaseORMService):
    BASE_MODEL = TelegramAccount

    async def delete_by_phone(self, phone: str, session: AsyncSession):
        await session.execute(delete(self.BASE_MODEL).where(self.BASE_MODEL.phone == phone))
        await session.commit()

    async def get_by_phone(self, phone: str, session: AsyncSession, *, throw_not_found: bool = True):
        query = await session.execute(select(self.BASE_MODEL).where(self.BASE_MODEL.phone == phone))
        result = query.fetchone()

        if result is None:
            if throw_not_found:
                raise Exception("Not found")
            return None

        obj = result[0]
        return obj


# TODO по хорошему надо бы singleton
class TelegramAccountsService(TelegramService):
    objects = _TelegramAccountsOrmService()
    client: TelegramClient = ...

    async def create_account(
        self,
        phone: str,
        code: str | None = None,
        code_hash: str | None = None,
        session: str | None = None,
        *,
        delete_if_exists=False
    ):
        """
        Create new client, sign in and create new Telegram Account with session
        """
        async with get_async_session() as db_session:
            if delete_if_exists:
                await self.objects.delete_by_phone(phone, db_session)

            new_account = TelegramAccount(
                phone=phone,
                code=code,
                code_hash=code_hash,
                session=session
            )

            await self.objects.save_and_refresh(new_account, db_session)

            if not new_account:
                raise Exception("Failed to create Telegram Account")

        return new_account

    async def sign_in_and_update_account(
        self,
        phone: str,
        code: str | None = None,
    ) -> tuple[failure_message | None, is_success]:
        """
        Create new client, sign in and create new Telegram Account with session
        """
        async with get_async_session() as db_session:
            account = await self.objects.get_by_phone(phone, db_session, throw_not_found=False)

            if account is None:
                logger.warn(f"Unknown phone: {phone}")
                return (f"Неизвестный телефон: {phone}", False)

            if not account.session:
                logger.error(f"Invalid session for {phone=}, session={account.session}")
                return (f"Ошибка сессии: {phone}", False)

            client = await self.create_new_client_and_connect(account.session)

            try:
                user = await client.sign_in(phone=phone, code=code, phone_code_hash=account.code_hash)

                await self.objects.update_instance_fields(
                    account, {"code": code, "session": client.session.save()},
                    save=True,
                    session=db_session
                )
                logger.info(
                    f"""
                    Success sign in account:
                        Name: {user.first_name} {user.last_name}
                        {phone=}
                        {code=}
                        code_hash={account.code_hash}
                    """
                )

            except PhoneCodeExpiredError:
                return (f"{phone}: код устарел", False)

            finally:
                await client.disconnect()

        return (None, True)

    @staticmethod
    def build_send_code_result_message(success: list[str], failure: list[str]):
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
            success_message_part
            + "\n"
            + failure_message_part
        )

    @staticmethod
    async def parse_phone_code_pairs_and_answer_if_errors(message: Message) -> list[PhoneCode]:
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
                result.append(PhoneCode(phone=pair[0], code=pair[1]))

            except:
                msg = f"Ошибка при сканировании пары: {pair}"

                logger.error(msg)
                await message.answer(msg)

        return result

    @staticmethod
    def build_sign_in_accounts_result_message(
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
            success_message_part
            + failure_message_part
            + remaining_message_part
        )
