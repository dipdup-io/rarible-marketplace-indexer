from typing import Type

from rarible_marketplace_indexer.types.tezos_objects.asset_value.asset_value import AssetValueField
from rarible_marketplace_indexer.types.tezos_objects.asset_value.base_value import BaseValue
from rarible_marketplace_indexer.types.tezos_objects.asset_value.base_value import DecimalNew


class Xtz(BaseValue):
    asset_max_digits: int = 36
    asset_precision: int = 6

    @staticmethod
    def from_u_tezos(value: DecimalNew):
        return Xtz(value) / 1_000_000


class XtzField(AssetValueField):
    python_class: Type[BaseValue] = Xtz
