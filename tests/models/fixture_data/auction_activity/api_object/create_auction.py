from datetime import datetime
from uuid import UUID

from pytz import UTC

from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.types.rarible_api_objects.activity.auction.activity import RaribleApiAuctionCreateActivity
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OperationHash

auction_activity_api_object = RaribleApiAuctionCreateActivity(
    id=UUID('9bbb97ee-877c-5b64-aa76-33dd730bafeb'),
    auction_id=UUID('1d1df503-0239-5a74-aae4-b86f375b6695'),
    network='ithacanet',
    source=PlatformEnum.RARIBLE,
    hash=OperationHash('opFJNJhaEzvzAv3AUHMjUwYAFjNUCGA1rsTHBsh6fcmiZfCXevF'),
    date=datetime(2022, 5, 3, 8, 9, 0, tzinfo=UTC),
    last_updated_at=datetime(2022, 5, 3, 8, 9, 0, tzinfo=UTC),
)
