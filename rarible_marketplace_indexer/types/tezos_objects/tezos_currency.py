from decimal import Context
from decimal import Decimal
from decimal import InvalidOperation
from functools import total_ordering
from typing import Any
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Type
from typing import Union

from tortoise import Model
from tortoise.fields import DecimalField

DecimalNew = Union[Decimal, float, str, Tuple[int, Sequence[int], int]]


@total_ordering
class AssetValue(Decimal):
    asset_max_digits = 96
    asset_precision: int = 36

    def __new__(cls, value: DecimalNew):
        ctx = Context(prec=cls.asset_max_digits + cls.asset_precision)
        asset_precision_mask: str = '1.' + '0' * (cls.asset_precision - 1) + '1'
        try:
            value = Decimal(value).quantize(Decimal(asset_precision_mask), context=ctx).normalize()
        except InvalidOperation:
            # covered in tests.asset.test_xtz.TestXtz.test_too_many_digits
            value = 0

        return Decimal.__new__(cls, value)

    def __str__(self) -> str:
        return f'{self:f}'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self})'

    def __eq__(self, other: DecimalNew) -> bool:
        cls = type(self)
        if not isinstance(other, cls):
            other = cls(other)
        return self.compare(other) == 0

    def __lt__(self, other):
        cls = type(self)
        if not isinstance(other, cls):
            other = cls(other)
        return self.compare(other) == -1


class Xtz(AssetValue):
    asset_max_digits = 36
    asset_precision: int = 6

    @staticmethod
    def from_u_tezos(value: DecimalNew):
        value = Decimal(value) / 1_000_000

        return Xtz(value)


class AssetValueField(DecimalField):
    python_class: Type[AssetValue] = AssetValue
    max_digits: int

    skip_to_python_if_native = False

    def __init__(self, **kwargs: Any) -> None:
        self.max_digits = self.python_class.asset_max_digits
        super().__init__(self.max_digits, self.python_class.asset_precision, **kwargs)

    def to_python_value(self, value: Any) -> Optional[Decimal]:

        if value is not None:
            value = self.python_class(value)
        self.validate(value)
        return value

    def to_db_value(self, value: Any, instance: Union[Type[Model], Model]) -> Any:
        if value is None:
            return None
        return str(value)


class XtzField(AssetValueField):
    python_class: Type[AssetValue] = Xtz
