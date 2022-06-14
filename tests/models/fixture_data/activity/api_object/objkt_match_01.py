from datetime import datetime
from uuid import UUID

from pytz import UTC

from rarible_marketplace_indexer.models import ActivityTypeEnum
from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.types.rarible_api_objects.activity.order.activity import RaribleApiOrderMatchActivity
from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset import TokenAsset
from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset import XtzAsset
from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset_type import MultiTokenAssetType
from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset_type import XtzAssetType
from rarible_marketplace_indexer.types.tezos_objects.asset_value.asset_value import AssetValue
from rarible_marketplace_indexer.types.tezos_objects.asset_value.xtz_value import Xtz
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OperationHash
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OriginatedAccountAddress

activity_api_object = RaribleApiOrderMatchActivity(
    id=UUID('45b51339-c32e-56ab-a44f-66463b7d4fad'),
    network='mainnet',
    type=ActivityTypeEnum.ORDER_MATCH,
    source=PlatformEnum.OBJKT,
    order_id=UUID('1603ff55-2507-5cba-b50c-3ae50162c5ee'),
    hash=OperationHash('oo4GwwjGX6RimeYBp68ddo1PS4aBc7ZpWDFmrqwZRcocnGykChm'),
    date=datetime(2021, 7, 1, 21, 9, 38, tzinfo=UTC),
    reverted=False,
    nft=TokenAsset(
        asset_type=MultiTokenAssetType(
            contract=OriginatedAccountAddress('KT1RJ6PbjHpwc3M5rw5s2Nbmefwbuwbdxton'),
            token_id='157097',
        ),
        asset_value=AssetValue(9),
    ),
    payment=XtzAsset(
        asset_type=XtzAssetType(),
        asset_value=Xtz(3),
    ),
    buyer=ImplicitAccountAddress('tz29tCQDFw8KwaMaBuroze6Sv2qd47nnP5Hv'),
    seller=ImplicitAccountAddress('tz1bn9ud4BmNGSCTWT86gB23ynR7tuWk8gAk'),
)
