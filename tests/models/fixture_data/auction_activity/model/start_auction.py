from datetime import datetime
from uuid import UUID

from pytz import UTC

from rarible_marketplace_indexer.models import ActivityTypeEnum
from rarible_marketplace_indexer.models import AuctionActivityModel
from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OperationHash

auction_activity_model = AuctionActivityModel(
    auction_id=UUID('1d1df503-0239-5a74-aae4-b86f375b6695'),
    type=ActivityTypeEnum.AUCTION_STARTED,
    network='ithacanet',
    platform=PlatformEnum.RARIBLE,
    internal_auction_id=123456,
    bid_value=None,
    bid_bidder=None,
    date=datetime(2022, 5, 3, 8, 9, 0, tzinfo=UTC),
    last_updated_at=datetime(2022, 5, 3, 8, 9, 0, tzinfo=UTC),
    operation_level=127001,
    operation_timestamp=datetime(2022, 5, 3, 8, 9, 0, tzinfo=UTC),
    operation_hash=OperationHash('opFJNJhaEzvzAv3AUHMjUwYAFjNUCGA1rsTHBsh6fcmiZfCXevF'),
    operation_counter=30182030,
    operation_nonce=1,
)
