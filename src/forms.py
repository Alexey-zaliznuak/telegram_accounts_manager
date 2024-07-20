from aiogram.filters.state import State, StatesGroup


class ImportAccountsForm(StatesGroup):
    send_phones = State()
    send_confirm_codes = State()
