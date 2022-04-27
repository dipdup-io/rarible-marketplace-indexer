from datetime import datetime

from pytz import UTC

from rarible_marketplace_indexer.models import ActivityTypeEnum
from rarible_marketplace_indexer.types.rarible_api_objects.activity.token.activity import RaribleApiTokenMintActivity
from rarible_marketplace_indexer.types.tezos_objects.asset_value.asset_value import AssetValue
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OriginatedAccountAddress

activity_api_object = RaribleApiTokenMintActivity(
    network='mainnet',
    type=ActivityTypeEnum.TOKEN_MINT,
    transfer_id=41354710,
    owner=ImplicitAccountAddress('tz1LaVcjZPWzVS8pa1nptgwKoSXRZ2dRQs6f'),
    contract=OriginatedAccountAddress('KT1DVkpd3UKJMe496e3fcB2ZZDjr1wvWPEcc'),
    token_id=47,
    value=AssetValue(10),
    transaction_id=41354703,
    date=datetime(2021, 2, 19, 4, 8, 36, tzinfo=UTC),
)
