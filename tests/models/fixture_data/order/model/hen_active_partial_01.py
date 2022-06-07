from datetime import datetime

from pytz import UTC

from rarible_marketplace_indexer.models import OrderModel
from rarible_marketplace_indexer.models import OrderStatusEnum
from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.types.rarible_api_objects.asset.enum import AssetClassEnum
from rarible_marketplace_indexer.types.tezos_objects.asset_value.asset_value import AssetValue
from rarible_marketplace_indexer.types.tezos_objects.asset_value.xtz_value import Xtz
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OriginatedAccountAddress

order_model = OrderModel(
    id=None,
    network='mainnet',
    fill='9',
    platform=PlatformEnum.HEN,
    internal_order_id='1354',
    status=OrderStatusEnum.ACTIVE,
    start_at=datetime(2021, 8, 9, 13, 7, 30, tzinfo=UTC),
    end_at=None,
    ended_at=None,
    make_stock=291,
    cancelled=False,
    salt=1207026,
    created_at=datetime(2021, 8, 9, 13, 7, 30, tzinfo=UTC),
    last_updated_at=datetime(2021, 8, 7, 15, 45, 46, tzinfo=UTC),
    make_price=Xtz(1),
    maker=ImplicitAccountAddress('tz2NY3Fgt5QufrYGP1JKdvLKcWWt86sLsqrS'),
    taker=None,
    make_asset_class=AssetClassEnum.MULTI_TOKEN,
    make_contract=OriginatedAccountAddress('KT1RJ6PbjHpwc3M5rw5s2Nbmefwbuwbdxton'),
    make_token_id='49575',
    make_value=AssetValue(300),
    take_asset_class=AssetClassEnum.XTZ,
    take_contract=None,
    take_token_id=None,
    take_value=Xtz(1),
)
