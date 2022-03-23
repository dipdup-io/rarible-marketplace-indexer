from decimal import Decimal
from decimal import InvalidOperation
from typing import Any
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Type
from typing import Union

from tortoise import Model
from tortoise.fields import DecimalField

DecimalNew = Union[Decimal, float, str, Tuple[int, Sequence[int], int]]


class AssetValue(Decimal):
    tezos_precision_mask: str = '1.000001'
    tezos_precision: int = 6

    def __new__(cls, value: DecimalNew):
        try:
            value = Decimal(value).quantize(Decimal(cls.tezos_precision_mask)).normalize()
        except InvalidOperation:
            # covered in tests.asset.test_xtz.TestXtz.test_too_many_digits
            value = 0

        return Decimal.__new__(cls, value)

    def __str__(self) -> str:
        return f'{self:f}'

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: DecimalNew) -> bool:
        cls = type(self)
        if not isinstance(other, cls):
            other = cls(other)
        return self.compare(other) == 0


class Xtz(AssetValue):
    def __repr__(self) -> str:
        return f'{self:f} ꜩ'

    @staticmethod
    def from_u_tezos(value: DecimalNew):
        value = Decimal(value) / 1000000

        return Xtz(value)


class AssetValueField(DecimalField):
    tezos_precision: int = 36
    max_digits: int = 96

    skip_to_python_if_native = False

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(self.max_digits, self.tezos_precision, **kwargs)

    def to_python_value(self, value: Any) -> Optional[Decimal]:

        if value is None:
            value = None
        else:
            value = AssetValue(value)
        self.validate(value)
        return value

    def to_db_value(self, value: Any, instance: Union[Type[Model], Model]) -> Any:
        if value is None:
            return None
        return str(value)


class XtzField(AssetValueField):
    def to_python_value(self, value: Any) -> Optional[Decimal]:

        if value is None:
            value = None
        else:
            value = Xtz(value)
        self.validate(value)
        return value
