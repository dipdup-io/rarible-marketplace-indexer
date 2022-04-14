import logging
from decimal import Decimal
from functools import wraps
from typing import Sequence
from typing import Tuple
from typing import Union

DecimalNew = Union[Decimal, float, str, Tuple[int, Sequence[int], int]]

decimal_return_methods = (
    '__abs__',
    '__add__',
    '__floordiv__',
    '__mod__',
    '__mul__',
    '__neg__',
    '__pos__',
    '__pow__',
    '__radd__',
    '__rfloordiv__',
    '__rmod__',
    '__rmul__',
    '__rsub__',
    '__rtruediv__',
    '__sub__',
    '__truediv__',
    'remainder_near',
    'real',
    'imag',
    'conjugate',
    '__round__',
    'fma',
    '__rpow__',
    'normalize',
    'quantize',
    'to_integral_exact',
    'to_integral_value',
    'to_integral',
    'sqrt',
    'max',
    'min',
    'canonical',
    'compare_signal',
    'compare_total',
    'compare_total_mag',
    'copy_abs',
    'copy_negate',
    'copy_sign',
    'exp',
    'ln',
    'log10',
    'logb',
    'logical_and',
    'logical_invert',
    'logical_or',
    'logical_xor',
    'max_mag',
    'min_mag',
    'next_minus',
    'next_plus',
    'next_toward',
    'radix',
    'rotate',
    'scaleb',
    'shift',
    '__copy__',
    '__deepcopy__',
)
decimal_comparison_methods = (
    '__eq__',
    '__lt__',
    '__le__',
    '__gt__',
    '__ge__',
    'compare',
)


class CustomDecimalMetaClass(type):
    def __init__(cls, name, bases, dct) -> None:
        super().__init__(name, bases, dct)
        for func_name in decimal_return_methods:
            setattr(cls, func_name, cls.return_decorator(getattr(bases[0], func_name)))
        for func_name in decimal_comparison_methods:
            setattr(cls, func_name, cls.other_decorator(getattr(bases[0], func_name)))

        cls._logger = logging.getLogger('CurrencyLogger')

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
        def wrapper(self, other):
            if not isinstance(other, self.__class__):
                other = self.__class__(other)
            result = method(self, other)
            return result

        return wrapper
