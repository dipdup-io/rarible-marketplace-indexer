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


class AbstractRaribleApiOrderActivity(AbstractRaribleApiObject):
    _kafka_topic = KafkaTopic.ACTIVITY_TOPIC
    type: str
    order_id: uuid.UUID
    source: PlatformEnum
    hash: OperationHash
    date: datetime
    reverted: bool = False


class RaribleApiOrderListActivity(AbstractRaribleApiOrderActivity):
    type: Literal[ActivityTypeEnum.ORDER_LIST, ActivityTypeEnum.MAKE_BID, ActivityTypeEnum.MAKE_FLOOR_BID] = ActivityTypeEnum.ORDER_LIST
    maker: ImplicitAccountAddress
    make: AbstractAsset
    take: Optional[AbstractAsset]
    price: Xtz


class RaribleApiOrderMatchActivity(AbstractRaribleApiOrderActivity):
    type: Literal[ActivityTypeEnum.ORDER_MATCH, ActivityTypeEnum.GET_BID, ActivityTypeEnum.GET_FLOOR_BID] = ActivityTypeEnum.ORDER_MATCH
    nft: AbstractAsset
    payment: Optional[AbstractAsset]
    buyer: ImplicitAccountAddress
    seller: ImplicitAccountAddress
    price: Xtz


class RaribleApiOrderCancelActivity(AbstractRaribleApiOrderActivity):
    type: Literal[
        ActivityTypeEnum.ORDER_CANCEL, ActivityTypeEnum.CANCEL_BID, ActivityTypeEnum.CANCEL_FLOOR_BID
    ] = ActivityTypeEnum.ORDER_CANCEL
    maker: ImplicitAccountAddress
    make: AbstractAsset
    take: Optional[AbstractAsset]


RaribleApiOrderActivity = Union[RaribleApiOrderListActivity, RaribleApiOrderMatchActivity, RaribleApiOrderCancelActivity]
