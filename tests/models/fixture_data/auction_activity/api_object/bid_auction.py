from datetime import datetime
from uuid import UUID

from pytz import UTC

from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.types.rarible_api_objects.activity.auction.activity import RaribleApiAuctionPutBidActivity
from rarible_marketplace_indexer.types.rarible_api_objects.auction.auction_bid import AuctionBid
from rarible_marketplace_indexer.types.tezos_objects.asset_value.asset_value import AssetValue
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OperationHash

auction_activity_api_object = RaribleApiAuctionPutBidActivity(
    id=UUID('03fa1145-08fc-58ae-8939-3b4e3b10d465'),
    auction_id=UUID('1d1df503-0239-5a74-aae4-b86f375b6695'),
    network='ithacanet',
    source=PlatformEnum.RARIBLE,
    hash=OperationHash('ooQohS1pjNehxAJZFoatr8qCXqNkYWC5ND8f17439PLQv72G4y9'),
    date=datetime(2022, 5, 3, 8, 10, 5, tzinfo=UTC),
    last_updated_at=datetime(2022, 5, 3, 8, 10, 5, tzinfo=UTC),
    bid=AuctionBid(
        buyer=ImplicitAccountAddress('tz1U6HmK5feYQ7VzrLdho7u5aRbBssNeMsU9'),
        amount=AssetValue(10),
        date=datetime(2022, 5, 3, 8, 10, 5, tzinfo=UTC),
    ),
)
