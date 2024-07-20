import logging
from typing import NamedTuple

from aiogram.types import Message

from core import TelegramService
from core.database.orm_service import BaseORMService
from core.types import FailureList, SuccessList
from core.utils import HTMLFormatter

from .models import TelegramAccount


logger = logging.getLogger(__name__)


class PhoneCodePair(NamedTuple):
    phone: str
    code: str


class TelegramAccountsService(TelegramService, BaseORMService):
    BASE_MODEL = TelegramAccount

    async def sign_in_and_save_account(pair: PhoneCodePair):
        pass

    def build_send_code_result_message(self, result: tuple[SuccessList[str], FailureList[str]]):
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

    async def parse_phone_code_pairs(self, message: Message) -> list[PhoneCodePair]:
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

    async def build_sign_in_accounts_result_message(
        self,
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
