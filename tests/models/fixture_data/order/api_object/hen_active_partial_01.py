from datetime import datetime
from uuid import UUID

from pytz import UTC

from rarible_marketplace_indexer.models import OrderStatusEnum
from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset import TokenAsset
from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset import XtzAsset
from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset_type import MultiTokenAssetType
from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset_type import XtzAssetType
from rarible_marketplace_indexer.types.rarible_api_objects.order.order import RaribleApiOrder
from rarible_marketplace_indexer.types.tezos_objects.asset_value.asset_value import AssetValue
from rarible_marketplace_indexer.types.tezos_objects.asset_value.xtz_value import Xtz
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OriginatedAccountAddress

order_api_object = RaribleApiOrder(
    id=UUID('1fa0e1f7-24c1-5cfe-bec8-af34cc7d69c2'),
    network='mainnet',
    fill=Xtz(9),
    platform=PlatformEnum.HEN,
    status=OrderStatusEnum.ACTIVE,
    started_at=datetime(2021, 8, 9, 13, 7, 30, tzinfo=UTC),
    ended_at=None,
    make_stock=AssetValue(291),
    cancelled=False,
    created_at=datetime(2021, 8, 9, 13, 7, 30, tzinfo=UTC),
    last_updated_at=datetime(2021, 8, 7, 15, 45, 46, tzinfo=UTC),
    make_price=Xtz(1),
    maker=ImplicitAccountAddress('tz2NY3Fgt5QufrYGP1JKdvLKcWWt86sLsqrS'),
    taker=None,
    make=TokenAsset(
        asset_type=MultiTokenAssetType(
            contract=OriginatedAccountAddress('KT1RJ6PbjHpwc3M5rw5s2Nbmefwbuwbdxton'),
            token_id='49575',
        ),
        asset_value=AssetValue(300),
    ),
    take=XtzAsset(
        asset_type=XtzAssetType(),
        asset_value=Xtz(1),
    ),
    salt=1207026,
)
