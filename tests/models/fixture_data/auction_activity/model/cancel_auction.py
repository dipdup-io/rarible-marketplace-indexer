from datetime import datetime
from uuid import UUID

from pytz import UTC

from rarible_marketplace_indexer.models import ActivityTypeEnum
from rarible_marketplace_indexer.models import AuctionActivityModel
from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OperationHash

auction_activity_model = AuctionActivityModel(
    auction_id=UUID('36d7c813-9bc6-5352-9ea4-e60c4c5947aa'),
    type=ActivityTypeEnum.AUCTION_CANCEL,
    network='ithacanet',
    platform=PlatformEnum.RARIBLE,
    internal_auction_id=123456,
    bid_value=None,
    bid_bidder=None,
    date=datetime(2022, 5, 3, 9, 10, 0, tzinfo=UTC),
    last_updated_at=datetime(2022, 5, 3, 9, 10, 0, tzinfo=UTC),
    operation_level=127001,
    operation_timestamp=datetime(2022, 5, 3, 9, 10, 0, tzinfo=UTC),
    operation_hash=OperationHash('ooSw6k8gJfdowJqHUPBJzS3W8jnkxj8f8sjh8ba4A219soahsjp'),
    operation_counter=30182030,
    operation_nonce=1,
)
