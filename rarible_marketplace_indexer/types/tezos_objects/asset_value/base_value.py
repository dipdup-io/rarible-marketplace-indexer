from decimal import Context
from decimal import Decimal
from decimal import InvalidOperation
from typing import Any
from typing import Optional
from typing import Type
from typing import Union

from tortoise.fields import DecimalField
from tortoise.models import Model

from rarible_marketplace_indexer.types.tezos_objects.asset_value.value_metaclass import CustomDecimalMetaClass
from rarible_marketplace_indexer.types.tezos_objects.asset_value.value_metaclass import DecimalNew


class BaseValue(Decimal, metaclass=CustomDecimalMetaClass):
    asset_max_digits: int
    asset_precision: int

    def __new__(cls, value: DecimalNew):
        if cls is BaseValue:
            raise NotImplementedError
        context = Context(prec=cls.asset_max_digits)
        asset_precision_exp = Decimal(f'1E-{cls.asset_precision}')
        try:
            value = Decimal(value)
            if value.to_integral(context=context) == value:
                value = value.quantize(Decimal(1))
            else:
                value = value.quantize(asset_precision_exp, context=context).normalize(context)

        except InvalidOperation:
            # covered in tests.asset.test_xtz.TestXtz.test_too_many_digits
            value = 0
            cls._logger.warning('Decimal Invalid Operation Error: too many digits')

        return Decimal.__new__(cls, value)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: DecimalNew):
        if not isinstance(value, cls):
            value = cls(value)

        return value

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self:f})'

    def __str__(self) -> str:
        return f'{self:f}'


class BaseValueField(DecimalField):
    python_class: Type[BaseValue]
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
