from datetime import datetime
from uuid import UUID

from pytz import UTC

from rarible_marketplace_indexer.models import ActivityTypeEnum
from rarible_marketplace_indexer.models import AuctionActivityModel
from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OperationHash

auction_activity_model = AuctionActivityModel(
    auction_id=UUID('f5f26042-cf6d-5b1b-9e64-30896b516356'),
    type=ActivityTypeEnum.AUCTION_FINISHED,
    network='ithacanet',
    platform=PlatformEnum.RARIBLE,
    internal_auction_id=123456,
    bid_value=None,
    bid_bidder=None,
    date=datetime(2022, 5, 3, 8, 32, 10, tzinfo=UTC),
    last_updated_at=datetime(2022, 5, 3, 8, 32, 10, tzinfo=UTC),
    operation_level=127001,
    operation_timestamp=datetime(2022, 5, 3, 8, 32, 10, tzinfo=UTC),
    operation_hash=OperationHash('opV3Rj694sqZPJboq9PvhJRDdyo8d5MQ3o8k7umeiunehu2tezx'),
    operation_counter=30182030,
    operation_nonce=1,
)
