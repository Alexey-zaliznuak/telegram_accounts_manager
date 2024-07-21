import logging
import asyncio
from pprint import pformat
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import F

from core.utils import HTMLFormatter

from .forms import ImportAccountsForm
from .service import TelegramAccountsService


router = Router()

service = TelegramAccountsService()
telegram_client = asyncio.run(service.create_new_client_and_connect())  # without sign in any accounts

logger = logging.getLogger(__name__)


SUCCESS_LIST_INDEX = 0  # TODO refactor with named tuple


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

    result = await service.request_code(telegram_client, phones)
    await state.update_data(phones=phones[SUCCESS_LIST_INDEX])

    await message.answer(
        service.build_send_code_result_message(result)
    )

    await state.set_state(ImportAccountsForm.send_phones)


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
    success_sign_in_phones: list[str] = []
    failure_sign_in_phones: list[str] = []

    for pair in pairs:
        if pair.phone not in remaining_phones:
            msg = f"Неопознанный телефон: {pair.phone}"

            await message.answer(msg)
            logger.warn(msg)

            continue

        try:
            await service.sign_in_and_save_account(pair)

            remaining_phones.remove(pair.phone)

            success_sign_in_phones.append(pair.phone)
            await state.update_data(phones=remaining_phones)

        except Exception as e:
            failure_sign_in_phones.append(pair.phone)

            msg = f"Ошибка при попытке залогиниться в аккаунт: {pair.phone}"

            await message.answer(msg)
            logger.error(msg + "\n" + str(e))

    await message.answer(
        main_telegram_service.build_sign_in_accounts_result_message(
            success_sign_in_phones,
            failure_sign_in_phones,
            remaining_phones,
        )
    )

    if not remaining_phones:
        await state.clear()
