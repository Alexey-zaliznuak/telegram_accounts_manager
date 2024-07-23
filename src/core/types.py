from typing import TypeAlias, TypeVar, NamedTuple


T = TypeVar('T')


SuccessList: TypeAlias = list[T]
FailureList: TypeAlias = list[T]


type phone_code_hash = str
type failure_message = str
type is_success = bool


class PhoneCode(NamedTuple):
    phone: str
    code: str


class TelegramSignInByPhoneAndCodeCredentials(NamedTuple):
    phone: str
    code: str
    phone_code_hash: str
