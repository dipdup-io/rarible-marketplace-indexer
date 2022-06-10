from datetime import datetime

from pytz import UTC

from rarible_marketplace_indexer.models import AuctionModel, AuctionStatusEnum
from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.types.rarible_api_objects.asset.enum import AssetClassEnum
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OriginatedAccountAddress

auction_model = AuctionModel(
            network="ithacanet",
            platform=PlatformEnum.RARIBLE,
            auction_id="1ed421e034a451d89ecb57f487595b28",
            status=AuctionStatusEnum.ACTIVE,
            start_at=datetime(2022, 5, 2, 15, 33, 35, tzinfo=UTC),
            ended_at=None,
            created_at=datetime(2022, 5, 2, 15, 33, 35, tzinfo=UTC),
            end_time=datetime(2022, 5, 2, 18, 20, 15, tzinfo=UTC),
            last_updated_at=datetime(2022, 5, 2, 15, 33, 35, tzinfo=UTC),
            ongoing=True,
            seller=ImplicitAccountAddress('tz1Mxsc66En4HsVHr6rppYZW82ZpLhpupToC'),
            sell_asset_class=AssetClassEnum.MULTI_TOKEN,
            sell_contract=OriginatedAccountAddress("KT1EreNsT2gXRvuTUrpx6Ju4WMug5xcEpr43"),
            sell_token_id="1",
            sell_value=1,
            buy_asset_class=AssetClassEnum.FUNGIBLE_TOKEN,
            buy_contract=None,
            buy_token_id=None,
            minimal_step=1,
            minimal_price=10,
            duration=1000,
            buy_price=100000,
            max_seller_fees=10000,
            last_bid_amount=None,
            last_bid_bidder=None,
            last_bid_date=None,
        )
