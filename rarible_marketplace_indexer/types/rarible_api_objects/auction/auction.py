from datetime import datetime
from typing import Optional

from humps.main import camelize

from rarible_marketplace_indexer.models import AuctionStatusEnum
from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.producer.const import KafkaTopic
from rarible_marketplace_indexer.types.rarible_api_objects import AbstractRaribleApiObject
from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset import AbstractAsset
from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset_description import AssetDescription
from rarible_marketplace_indexer.types.rarible_api_objects.auction.auction_bid import AuctionBid
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OriginatedAccountAddress


class RaribleApiAuction(AbstractRaribleApiObject):
    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True
        use_enum_values = True

    _kafka_topic = KafkaTopic.AUCTION_TOPIC
    platform: PlatformEnum
    contract: OriginatedAccountAddress
    seller: ImplicitAccountAddress
    sell: AbstractAsset
    buy: AssetDescription
    end_time: Optional[datetime]
    minimal_step: int
    minimal_price: int
    created_at: datetime
    last_updated_at: datetime
    buy_price: int
    status: AuctionStatusEnum
    ongoing: bool
    hash: str
    start_at: datetime
    auction_id: str
    last_bid: Optional[AuctionBid]
