from datetime import datetime

from pytz import UTC

from rarible_marketplace_indexer.models import ActivityTypeEnum
from rarible_marketplace_indexer.types.rarible_api_objects.activity.token.activity import RaribleApiTokenTransferActivity
from rarible_marketplace_indexer.types.tezos_objects.asset_value.asset_value import AssetValue
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OriginatedAccountAddress

activity_api_object = RaribleApiTokenTransferActivity(
    network='mainnet',
    type=ActivityTypeEnum.TOKEN_TRANSFER,
    transfer_id=62734941,
    transfer_from=ImplicitAccountAddress('tz1Zw7KfW7y9TT1p5vNDHf2sehmQXefhyzwg'),
    owner=ImplicitAccountAddress('KT1HbQepzV1nVGg8QVznG7z4RcHseD5kwqBn'),
    contract=OriginatedAccountAddress('KT1RJ6PbjHpwc3M5rw5s2Nbmefwbuwbdxton'),
    token_id=165879,
    value=AssetValue(1),
    transaction_id=62734842,
    date=datetime(2021, 7, 12, 18, 1, 18, tzinfo=UTC),
)
