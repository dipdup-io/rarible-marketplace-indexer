from datetime import datetime
from uuid import UUID

from pytz import UTC

from rarible_marketplace_indexer.models import ActivityModel
from rarible_marketplace_indexer.models import ActivityTypeEnum
from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.types.rarible_api_objects.asset.enum import AssetClassEnum
from rarible_marketplace_indexer.types.tezos_objects.asset_value.xtz_value import Xtz
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OperationHash
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OriginatedAccountAddress

activity_model = ActivityModel(
    type=ActivityTypeEnum.ORDER_MATCH,
    network='mainnet',
    platform=PlatformEnum.OBJKT,
    order_id=UUID('1603ff55-2507-5cba-b50c-3ae50162c5ee'),
    internal_order_id=145,
    maker=ImplicitAccountAddress('tz1bn9ud4BmNGSCTWT86gB23ynR7tuWk8gAk'),
    taker=ImplicitAccountAddress('tz29tCQDFw8KwaMaBuroze6Sv2qd47nnP5Hv'),
    make_asset_class=AssetClassEnum.MULTI_TOKEN,
    make_contract=OriginatedAccountAddress('KT1RJ6PbjHpwc3M5rw5s2Nbmefwbuwbdxton'),
    make_token_id=157097,
    make_value=9,
    take_asset_class=AssetClassEnum.XTZ,
    take_contract=None,
    take_token_id=None,
    take_value=Xtz(3),
    operation_level=127001,
    operation_timestamp=datetime(2021, 7, 1, 21, 9, 38, tzinfo=UTC),
    operation_hash=OperationHash('oo4GwwjGX6RimeYBp68ddo1PS4aBc7ZpWDFmrqwZRcocnGykChm'),
    operation_counter=30182030,
    operation_nonce=1,
)
