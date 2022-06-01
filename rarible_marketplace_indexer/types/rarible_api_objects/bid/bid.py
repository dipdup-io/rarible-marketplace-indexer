from datetime import datetime
from typing import Optional

from humps.main import camelize

from rarible_marketplace_indexer.models import OrderStatusEnum
from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.producer.const import KafkaTopic
from rarible_marketplace_indexer.types.rarible_api_objects import AbstractRaribleApiObject
from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset import AbstractAsset
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress


class RaribleApiBid(AbstractRaribleApiObject):
    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True
        use_enum_values = True

    _kafka_topic = KafkaTopic.ORDER_TOPIC
    platform: PlatformEnum
    status: OrderStatusEnum
    ended_at: Optional[datetime]
    created_at: datetime
    last_updated_at: datetime
    maker: Optional[ImplicitAccountAddress]
    taker: Optional[ImplicitAccountAddress]
    make: AbstractAsset
    take: Optional[AbstractAsset]
