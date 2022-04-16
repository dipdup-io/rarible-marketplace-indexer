from datetime import datetime
from typing import Optional

from pydantic.dataclasses import dataclass

from rarible_marketplace_indexer.types.tezos_objects.asset_value.asset_value import AssetValue
from rarible_marketplace_indexer.types.tezos_objects.asset_value.xtz_value import Xtz
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OriginatedAccountAddress


@dataclass
class ListDto:
    internal_order_id: str
    maker: ImplicitAccountAddress
    contract: OriginatedAccountAddress
    token_id: int
    amount: AssetValue
    object_price: Xtz
    started_at: Optional[datetime] = None  # for marketplaces with the possibility of a delayed start of sales
    ended_at: Optional[datetime] = None  # for marketplaces with the possibility of sales expiration


@dataclass
class CancelDto:
    internal_order_id: str


@dataclass
class MatchDto:
    internal_order_id: str
    match_amount: AssetValue
    match_timestamp: datetime
