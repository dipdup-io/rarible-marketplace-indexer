from datetime import datetime
from uuid import UUID

from pytz import UTC

from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.types.rarible_api_objects.activity.auction.activity import RaribleApiAuctionCancelActivity
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OperationHash

auction_activity_api_object = RaribleApiAuctionCancelActivity(
    id=UUID('417b7587-a82a-5d61-93da-bc37dc717bce'),
    auction_id=UUID('36d7c813-9bc6-5352-9ea4-e60c4c5947aa'),
    network='ithacanet',
    source=PlatformEnum.RARIBLE,
    hash=OperationHash('ooSw6k8gJfdowJqHUPBJzS3W8jnkxj8f8sjh8ba4A219soahsjp'),
    date=datetime(2022, 5, 3, 9, 10, 0, tzinfo=UTC),
    last_updated_at=datetime(2022, 5, 3, 9, 10, 0, tzinfo=UTC),
)
