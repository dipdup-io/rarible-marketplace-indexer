from typing import Any
from typing import Sequence
from typing import Union
from typing import no_type_check

from pydantic.validators import str_validator
from tortoise.fields import CharField
from tortoise.validators import MinLengthValidator


class TezosObjectHash(str):
    length: int = NotImplemented
    header: Union[str, tuple[str, ...]] = NotImplemented

    @no_type_check
    def __new__(cls, address: str, **kwargs) -> 'TezosObjectHash':
        if cls is TezosObjectHash:
            raise NotImplementedError
        return str.__new__(cls, address)

    @classmethod
    def validate(cls, value: Any) -> 'TezosObjectHash':
        if len(value) != cls.length:
            raise ValueError
        if not value.startswith(cls.header):
            raise ValueError

        if value.__class__ == cls:
            return value

        value = str_validator(value)
        value = value.strip()

        return cls(value)


class OperationHash(TezosObjectHash):
    length: int = 51
    header: str = 'o'


class AccountAddress(TezosObjectHash):

    length: int = 36

    def __new__(cls, address: str, **kwargs) -> 'TezosObjectHash':
        if cls is AccountAddress:
            raise NotImplementedError
        return super().__new__(cls, address, **kwargs)


class ImplicitAccountAddress(AccountAddress):
    header: Sequence = ('tz1', 'tz2', 'tz3')


class OriginatedAccountAddress(AccountAddress):
    header: str = 'KT1'


class OperationHashField(CharField):
    length: int = OperationHash.length

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(self.length, **kwargs)
        self.validators.append(MinLengthValidator(self.length))


class AccountAddressField(CharField):
    length: int = AccountAddress.length

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(self.length, **kwargs)
        self.validators.append(MinLengthValidator(self.length))
