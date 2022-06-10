from datetime import datetime
from uuid import UUID

from pytz import UTC

from rarible_marketplace_indexer.models import ActivityTypeEnum
from rarible_marketplace_indexer.models import AuctionActivityModel
from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.types.tezos_objects.asset_value.asset_value import AssetValue
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OperationHash

auction_activity_model = AuctionActivityModel(
    auction_id=UUID('1d1df503-0239-5a74-aae4-b86f375b6695'),
    type=ActivityTypeEnum.AUCTION_BID,
    network='ithacanet',
    platform=PlatformEnum.RARIBLE,
    internal_auction_id=123456,
    bid_value=AssetValue(10),
    bid_bidder=ImplicitAccountAddress('tz1U6HmK5feYQ7VzrLdho7u5aRbBssNeMsU9'),
    date=datetime(2022, 5, 3, 8, 10, 5, tzinfo=UTC),
    last_updated_at=datetime(2022, 5, 3, 8, 10, 5, tzinfo=UTC),
    operation_level=127001,
    operation_timestamp=datetime(2022, 5, 3, 8, 10, 5, tzinfo=UTC),
    operation_hash=OperationHash('ooQohS1pjNehxAJZFoatr8qCXqNkYWC5ND8f17439PLQv72G4y9'),
    operation_counter=30182030,
    operation_nonce=1,
)
