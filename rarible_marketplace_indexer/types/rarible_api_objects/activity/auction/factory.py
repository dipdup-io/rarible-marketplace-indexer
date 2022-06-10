from typing import Callable
from typing import Dict

from rarible_marketplace_indexer.models import ActivityTypeEnum
from rarible_marketplace_indexer.models import AuctionActivityModel
from rarible_marketplace_indexer.types.rarible_api_objects.activity.auction.activity import RaribleApiAuctionActivity
from rarible_marketplace_indexer.types.rarible_api_objects.activity.auction.activity import RaribleApiAuctionCancelActivity
from rarible_marketplace_indexer.types.rarible_api_objects.activity.auction.activity import RaribleApiAuctionCreateActivity
from rarible_marketplace_indexer.types.rarible_api_objects.activity.auction.activity import RaribleApiAuctionEndActivity
from rarible_marketplace_indexer.types.rarible_api_objects.activity.auction.activity import RaribleApiAuctionFinishActivity
from rarible_marketplace_indexer.types.rarible_api_objects.activity.auction.activity import RaribleApiAuctionPutBidActivity
from rarible_marketplace_indexer.types.rarible_api_objects.activity.auction.activity import RaribleApiAuctionStartActivity
from rarible_marketplace_indexer.types.rarible_api_objects.auction.auction_bid import AuctionBid


class RaribleApiAuctionActivityFactory:
    @classmethod
    def _build_auction_start_activity(cls, activity: AuctionActivityModel) -> RaribleApiAuctionStartActivity:
        return RaribleApiAuctionStartActivity(
            id=activity.id,
            auction_id=activity.auction_id,
            network=activity.network,
            source=activity.platform,
            hash=activity.operation_hash,
            date=activity.operation_timestamp,
            last_updated_at=activity.last_updated_at,
        )

    @classmethod
    def _build_auction_create_activity(cls, activity: AuctionActivityModel) -> RaribleApiAuctionCreateActivity:
        return RaribleApiAuctionCreateActivity(
            id=activity.id,
            auction_id=activity.auction_id,
            network=activity.network,
            source=activity.platform,
            hash=activity.operation_hash,
            date=activity.operation_timestamp,
            last_updated_at=activity.last_updated_at,
        )

    @classmethod
    def _build_auction_put_bid_activity(cls, activity: AuctionActivityModel) -> RaribleApiAuctionPutBidActivity:
        return RaribleApiAuctionPutBidActivity(
            id=activity.id,
            auction_id=activity.auction_id,
            network=activity.network,
            source=activity.platform,
            hash=activity.operation_hash,
            date=activity.operation_timestamp,
            last_updated_at=activity.last_updated_at,
            bid=AuctionBid(buyer=activity.bid_bidder, amount=activity.bid_value, date=activity.date),
        )

    @classmethod
    def _build_auction_cancel_activity(cls, activity: AuctionActivityModel) -> RaribleApiAuctionCancelActivity:
        return RaribleApiAuctionCancelActivity(
            id=activity.id,
            auction_id=activity.auction_id,
            network=activity.network,
            source=activity.platform,
            hash=activity.operation_hash,
            date=activity.operation_timestamp,
            last_updated_at=activity.last_updated_at,
        )

    @classmethod
    def _build_auction_finish_activity(cls, activity: AuctionActivityModel) -> RaribleApiAuctionFinishActivity:
        return RaribleApiAuctionFinishActivity(
            id=activity.id,
            auction_id=activity.auction_id,
            network=activity.network,
            source=activity.platform,
            hash=activity.operation_hash,
            date=activity.operation_timestamp,
            last_updated_at=activity.last_updated_at,
        )

    @classmethod
    def _build_auction_end_activity(cls, activity: AuctionActivityModel) -> RaribleApiAuctionEndActivity:
        return RaribleApiAuctionEndActivity(
            id=activity.id,
            auction_id=activity.auction_id,
            network=activity.network,
            source=activity.platform,
            hash=activity.operation_hash,
            date=activity.operation_timestamp,
            last_updated_at=activity.last_updated_at,
        )

    @classmethod
    def _get_factory_method(cls, activity: AuctionActivityModel) -> callable:
        method_map: Dict[ActivityTypeEnum, Callable[[AuctionActivityModel], callable]] = {
            ActivityTypeEnum.AUCTION_CREATED: cls._build_auction_create_activity,
            ActivityTypeEnum.AUCTION_STARTED: cls._build_auction_start_activity,
            ActivityTypeEnum.AUCTION_BID: cls._build_auction_put_bid_activity,
            ActivityTypeEnum.AUCTION_CANCEL: cls._build_auction_cancel_activity,
            ActivityTypeEnum.AUCTION_FINISHED: cls._build_auction_finish_activity,
            ActivityTypeEnum.AUCTION_ENDED: cls._build_auction_end_activity,
        }

        return method_map.get(activity.type, cls._build_auction_start_activity)

    @classmethod
    def build(cls, activity: AuctionActivityModel) -> RaribleApiAuctionActivity:
        factory_method = cls._get_factory_method(activity)

        return factory_method(activity)
