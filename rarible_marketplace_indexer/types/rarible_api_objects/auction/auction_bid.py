from datetime import datetime

from humps.main import camelize
from pydantic import BaseModel

from rarible_marketplace_indexer.types.tezos_objects.asset_value.asset_value import AssetValue
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress


class AuctionBid(BaseModel):
    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True

    buyer: ImplicitAccountAddress
    amount: AssetValue
    date: datetime
