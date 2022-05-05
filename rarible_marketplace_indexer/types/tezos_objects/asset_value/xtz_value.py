from typing import Type

from rarible_marketplace_indexer.types.tezos_objects.asset_value.base_value import BaseValue
from rarible_marketplace_indexer.types.tezos_objects.asset_value.base_value import BaseValueField
from rarible_marketplace_indexer.types.tezos_objects.asset_value.value_metaclass import DecimalNew


class Xtz(BaseValue):
    asset_max_digits: int = 176
    asset_precision: int = 6

    @staticmethod
    def from_u_tezos(value: DecimalNew):
        value = Xtz(value)
        if value.to_integral() != value:
            raise ValueError(f'uTezos must be integer value, {value} given')
        return value / 1_000_000


class XtzField(BaseValueField):
    python_class: Type[BaseValue] = Xtz
