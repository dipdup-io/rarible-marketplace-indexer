from typing import Type

from rarible_marketplace_indexer.types.tezos_objects.asset_value.base_value import BaseValue
from rarible_marketplace_indexer.types.tezos_objects.asset_value.base_value import BaseValueField


class AssetValue(BaseValue):
    asset_max_digits: int = 176
    asset_precision: int = 36


class AssetValueField(BaseValueField):
    python_class: Type[AssetValue] = AssetValue
