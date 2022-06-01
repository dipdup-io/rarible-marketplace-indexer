from datetime import datetime

from pytz import UTC

from rarible_marketplace_indexer.models import BidModel
from rarible_marketplace_indexer.models import OrderStatusEnum
from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.types.rarible_api_objects.asset.enum import AssetClassEnum
from rarible_marketplace_indexer.types.tezos_objects.asset_value.asset_value import AssetValue
from rarible_marketplace_indexer.types.tezos_objects.asset_value.xtz_value import Xtz
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OriginatedAccountAddress

bid_model = BidModel(
    id=None,
    network='ithacanet',
    platform=PlatformEnum.RARIBLE,
    internal_order_id='21325dffc35b5a5ba66ed8eab81edb90',
    status=OrderStatusEnum.ACTIVE,
    ended_at=None,
    created_at=datetime(2022, 6, 1, 10, 12, 15, tzinfo=UTC),
    last_updated_at=datetime(2022, 6, 1, 10, 12, 15, tzinfo=UTC),
    bidder=ImplicitAccountAddress('tz1U6HmK5feYQ7VzrLdho7u5aRbBssNeMsU9'),
    seller=None,
    make_asset_class=AssetClassEnum.MULTI_TOKEN,
    make_contract=OriginatedAccountAddress('KT1Uke8qc4YTfP41dGuoGC8UsgRyCtyvKPLA'),
    make_token_id='175',
    make_value=AssetValue(1),
    take_asset_class=AssetClassEnum.XTZ,
    take_contract=None,
    take_token_id=None,
    take_value=Xtz(0.1),
)
