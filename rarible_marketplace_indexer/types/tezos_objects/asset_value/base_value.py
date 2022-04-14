import decimal
import logging
from decimal import Context
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

from decimal import Decimal
from functools import wraps


class CustomDecimalMetaClass(type):
    def __init__(cls, name, bases, dct) -> None:
        super().__init__(name, bases, dct)
        for func_name in cls.get_return_methods():
            setattr(cls, func_name, cls.return_decorator(getattr(bases[0], func_name)))
        for func_name in cls.get_comparsion_methods():
            setattr(cls, func_name, cls.other_decorator(getattr(bases[0], func_name)))

        cls._logger = logging.getLogger('CurrencyLogger')

    @staticmethod
    def get_return_methods():
        for item_name in (
            '__abs__', '__add__', '__floordiv__', '__mod__', '__mul__', '__neg__', '__pos__', '__pow__', '__radd__', '__rfloordiv__', '__rmod__', '__rmul__', '__rsub__', '__rtruediv__', '__sub__', '__truediv__', 'remainder_near', 'real', 'imag', 'conjugate', '__round__', 'fma', '__rpow__', 'normalize', 'quantize', 'to_integral_exact', 'to_integral_value', 'to_integral', 'sqrt', 'max', 'min', 'canonical', 'compare_signal', 'compare_total', 'compare_total_mag', 'copy_abs', 'copy_negate', 'copy_sign', 'exp', 'ln', 'log10', 'logb', 'logical_and', 'logical_invert', 'logical_or', 'logical_xor', 'max_mag', 'min_mag', 'next_minus', 'next_plus', 'next_toward', 'radix', 'rotate', 'scaleb', 'shift', '__copy__', '__deepcopy__', '_rescale',
        ):
            yield item_name

    @staticmethod
    def get_comparsion_methods():
        for item_name in (
            '__eq__', '__lt__', '__le__', '__gt__', '__ge__', 'compare',
        ):
            yield item_name


    @staticmethod
    def return_decorator(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            result = method(self, *args, **kwargs)
            if not isinstance(result, self.__class__):
                result = self.__class__(result)
            return result

        return wrapper


    @staticmethod
    def other_decorator(method):
        @wraps(method)
        def wrapper(self, other, context=None):
            if not isinstance(other, self.__class__):
                other = self.__class__(other)
            result = method(self, other, context=context)
            return result

        return wrapper


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
