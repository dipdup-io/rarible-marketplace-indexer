from datetime import datetime

from pytz import UTC

from rarible_marketplace_indexer.models import ActivityTypeEnum
from rarible_marketplace_indexer.types.rarible_api_objects.activity.token.activity import RaribleApiTokenBurnActivity
from rarible_marketplace_indexer.types.tezos_objects.asset_value.asset_value import AssetValue
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OriginatedAccountAddress

activity_api_object = RaribleApiTokenBurnActivity(
    network='mainnet',
    type=ActivityTypeEnum.TOKEN_BURN,
    transfer_id=205699817,
    owner=ImplicitAccountAddress('tz1gs8ewUnVXgAdaBdZmF4q6su6PZ5vWgaCe'),
    contract=OriginatedAccountAddress('KT18pVpRXKPY2c4U2yFEGSH3ZnhB2kL8kwXS'),
    token_id=58000,
    value=AssetValue(10),
    transaction_id=205699797,
    date=datetime(2022, 4, 14, 8, 24, 29, tzinfo=UTC),
)
