import uuid
from datetime import datetime
from typing import Literal
from typing import Optional
from typing import Union

from rarible_marketplace_indexer.models import ActivityTypeEnum
from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.producer.const import KafkaTopic
from rarible_marketplace_indexer.types.rarible_api_objects import AbstractRaribleApiObject
from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset import AbstractAsset
from rarible_marketplace_indexer.types.tezos_objects.asset_value.xtz_value import Xtz
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OperationHash


class AbstractRaribleApiActivity(AbstractRaribleApiObject):
    _kafka_topic = KafkaTopic.ACTIVITY_TOPIC
    type: str
    order_id: uuid.UUID
    source: PlatformEnum
    hash: OperationHash
    date: datetime
    reverted: bool = False


class RaribleApiListActivity(AbstractRaribleApiActivity):
    type: Literal[ActivityTypeEnum.LIST] = ActivityTypeEnum.LIST
    maker: ImplicitAccountAddress
    make: AbstractAsset
    take: Optional[AbstractAsset]
    price: Xtz


class RaribleApiMatchActivity(AbstractRaribleApiActivity):
    type: Literal[ActivityTypeEnum.MATCH] = ActivityTypeEnum.MATCH
    nft: AbstractAsset
    payment: Optional[AbstractAsset]
    buyer: ImplicitAccountAddress
    seller: ImplicitAccountAddress
    price: Xtz


class RaribleApiCancelActivity(AbstractRaribleApiActivity):
    type: Literal[ActivityTypeEnum.CANCEL] = ActivityTypeEnum.CANCEL
    maker: ImplicitAccountAddress
    make: AbstractAsset
    take: Optional[AbstractAsset]


RaribleApiActivity = Union[RaribleApiListActivity, RaribleApiMatchActivity, RaribleApiCancelActivity]
