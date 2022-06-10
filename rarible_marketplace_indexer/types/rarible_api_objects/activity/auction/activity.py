import uuid
from datetime import datetime
from typing import Literal
from typing import Union

from rarible_marketplace_indexer.models import ActivityTypeEnum
from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.producer.const import KafkaTopic
from rarible_marketplace_indexer.types.rarible_api_objects import AbstractRaribleApiObject
from rarible_marketplace_indexer.types.rarible_api_objects.auction.auction_bid import AuctionBid
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OperationHash


class AbstractRaribleApiAuctionActivity(AbstractRaribleApiObject):
    _kafka_topic = KafkaTopic.AUCTION_ACTIVITY_TOPIC
    type: str
    auction_id: uuid.UUID
    source: PlatformEnum
    hash: OperationHash
    date: datetime
    last_updated_at: datetime
    reverted: bool = False


class RaribleApiAuctionStartActivity(AbstractRaribleApiAuctionActivity):
    type: Literal[ActivityTypeEnum.AUCTION_STARTED] = ActivityTypeEnum.AUCTION_STARTED


class RaribleApiAuctionCreateActivity(AbstractRaribleApiAuctionActivity):
    type: Literal[ActivityTypeEnum.AUCTION_CREATED] = ActivityTypeEnum.AUCTION_CREATED


class RaribleApiAuctionPutBidActivity(AbstractRaribleApiAuctionActivity):
    type: Literal[ActivityTypeEnum.AUCTION_BID] = ActivityTypeEnum.AUCTION_BID
    bid: AuctionBid


class RaribleApiAuctionCancelActivity(AbstractRaribleApiAuctionActivity):
    type: Literal[ActivityTypeEnum.AUCTION_CANCEL] = ActivityTypeEnum.AUCTION_CANCEL


class RaribleApiAuctionFinishActivity(AbstractRaribleApiAuctionActivity):
    type: Literal[ActivityTypeEnum.AUCTION_FINISHED] = ActivityTypeEnum.AUCTION_FINISHED


class RaribleApiAuctionEndActivity(AbstractRaribleApiAuctionActivity):
    type: Literal[ActivityTypeEnum.AUCTION_ENDED] = ActivityTypeEnum.AUCTION_ENDED


RaribleApiAuctionActivity = Union[
    RaribleApiAuctionStartActivity,
    RaribleApiAuctionPutBidActivity,
    RaribleApiAuctionCancelActivity,
    RaribleApiAuctionFinishActivity,
    RaribleApiAuctionCreateActivity,
    RaribleApiAuctionEndActivity,
]
