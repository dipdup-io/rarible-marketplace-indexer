from datetime import datetime
from uuid import UUID

from pytz import UTC

from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.types.rarible_api_objects.activity.auction.activity import RaribleApiAuctionFinishActivity
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OperationHash

auction_activity_api_object = RaribleApiAuctionFinishActivity(
    id=UUID('bfd61bb9-5348-5a1c-91a9-9f4d35c2cdf1'),
    auction_id=UUID('f5f26042-cf6d-5b1b-9e64-30896b516356'),
    network='ithacanet',
    source=PlatformEnum.RARIBLE,
    hash=OperationHash('opV3Rj694sqZPJboq9PvhJRDdyo8d5MQ3o8k7umeiunehu2tezx'),
    date=datetime(2022, 5, 3, 8, 32, 10, tzinfo=UTC),
    last_updated_at=datetime(2022, 5, 3, 8, 32, 10, tzinfo=UTC),
)
