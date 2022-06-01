from datetime import datetime
from uuid import UUID

from pytz import UTC

from rarible_marketplace_indexer.models import OrderStatusEnum
from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset import TokenAsset
from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset import XtzAsset
from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset_type import MultiTokenAssetType
from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset_type import XtzAssetType
from rarible_marketplace_indexer.types.rarible_api_objects.bid.bid import RaribleApiBid
from rarible_marketplace_indexer.types.tezos_objects.asset_value.asset_value import AssetValue
from rarible_marketplace_indexer.types.tezos_objects.asset_value.xtz_value import Xtz
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OriginatedAccountAddress

bid_api_object = RaribleApiBid(
    id=UUID('f2e5cd60-8c23-521d-b7c6-881d59e1c6fb'),
    network='ithacanet',
    platform=PlatformEnum.RARIBLE,
    status=OrderStatusEnum.ACTIVE,
    ended_at=None,
    created_at=datetime(2022, 6, 1, 10, 12, 15, tzinfo=UTC),
    last_updated_at=datetime(2022, 6, 1, 10, 12, 15, tzinfo=UTC),
    bidder=ImplicitAccountAddress('tz1U6HmK5feYQ7VzrLdho7u5aRbBssNeMsU9'),
    seller=None,
    make=TokenAsset(
        asset_type=MultiTokenAssetType(
            contract=OriginatedAccountAddress('KT1Uke8qc4YTfP41dGuoGC8UsgRyCtyvKPLA'),
            token_id='175',
        ),
        asset_value=AssetValue(1),
    ),
    take=XtzAsset(
        asset_type=XtzAssetType(),
        asset_value=Xtz(0.01),
    )
)
