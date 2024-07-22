import logging
import asyncio
from pprint import pformat
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import F

from core.utils import HTMLFormatter
from telethon.errors import FloodError

from .forms import ImportAccountsForm
from .service import TelegramAccountsService


router = Router()
logger = logging.getLogger(__name__)

service = TelegramAccountsService()
telegram_client = service.create_new_client()  # without sign in any accounts


SUCCESS_LIST_INDEX = 0  # TODO refactor with named tuple


# TODO admins middleware
# TODO commands for set unsold / sold states
# TODO commands for clearing not cleared accounts
# TODO commands for force clearing any accounts
# TODO добавить ошибки текстом

@router.message(Command("import"))
async def start_import(message: Message, state: FSMContext):
    await message.answer("Введите номер телефона:")
    await state.set_state(ImportAccountsForm.send_phones)


@router.message(F.text, ImportAccountsForm.send_phones)
async def send_phones(message: Message, state: FSMContext):
    phones = list(set(message.text.splitlines()))
    logger.info(f"Start getting codes for phones: {pformat(phones)}")

    await message.answer(
        "Начинаю запрашивать коды для следующих телефонов:" + "\n\n"
        + "\n".join([HTMLFormatter.code(phone) for phone in phones])
    )

    success = []
    failure = []

    for phone in phones:
        result, is_success = await service.request_code(phone, telegram_client)

        if not is_success:
            failure.append(result)
            logger.error(f"Failed to send code, {phone=}, {result=}")
            continue

        await service.create_account(
            phone=result.phone,
            code=None,
            code_hash=result.code_hash,
            delete_if_exists=True,
        )

        success.append(result.phone)
        await state.update_data(phones=success)

    await message.answer(service.build_send_code_result_message(success, failure))

    await state.set_state(ImportAccountsForm.send_confirm_codes)


@router.message(Command("end_import"), ImportAccountsForm.send_confirm_codes)
async def end_import(message: Message, state: FSMContext):
    """
    Use for skip not confirmed codes and clear state.
    Can be useful if part of uploaded phones became unavailable
    """
    await message.answer("Оставшиеся аккаунты пропущены")
    await state.clear()


@router.message(F.text, ImportAccountsForm.send_confirm_codes)
async def send_codes(message: Message, state: FSMContext):
    """
    Get codes in format:
    ```
    <phone> <code>
    <phone> <code>
    ```
    """

    pairs = await service.parse_phone_code_pairs_and_answer_if_errors(message)

    state_data = await state.get_data()
    remaining_phones: list[str] = state_data.get("phones")

    success_phones: list[str] = []
    failure_sign_in_phones: list[str] = []

    for pair in pairs:
        if pair.phone not in remaining_phones:
            msg = f"Неопознанный телефон: {pair.phone}"
            await message.answer(msg)
            logger.warn(msg)
            continue

        await service.sign_in_and_update_account(pair, delete_if_exists=True)

        remaining_phones.remove(pair.phone)
        success_phones.append(pair.phone)

        await state.update_data(phones=remaining_phones)

    await message.answer(
        service.build_sign_in_accounts_result_message(
            success_phones,
            failure_sign_in_phones,
            remaining_phones,
        )
    )

    if not remaining_phones:
        await state.clear()
