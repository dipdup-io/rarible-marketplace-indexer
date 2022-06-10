from datetime import datetime
from uuid import UUID

from pytz import UTC

from rarible_marketplace_indexer.models import AuctionStatusEnum
from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset import TokenAsset
from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset_description import AssetDescription
from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset_type import MultiTokenAssetType
from rarible_marketplace_indexer.types.rarible_api_objects.asset.enum import AssetClassEnum
from rarible_marketplace_indexer.types.rarible_api_objects.auction.auction import RaribleApiAuction
from rarible_marketplace_indexer.types.rarible_api_objects.auction.auction_bid import AuctionBid
from rarible_marketplace_indexer.types.tezos_objects.asset_value.asset_value import AssetValue
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OriginatedAccountAddress

auction_api_object = RaribleApiAuction(
            id=UUID("427d1b55-fff3-5af7-ad49-6d817b0f7d14"),
            platform=PlatformEnum.RARIBLE,
            network="ithacanet",
            contract=OriginatedAccountAddress("KT1EreNsT2gXRvuTUrpx6Ju4WMug5xcEpr43"),
            seller=ImplicitAccountAddress('tz1Mxsc66En4HsVHr6rppYZW82ZpLhpupToC'),
            sell=TokenAsset(
                _asset_class=AssetClassEnum.MULTI_TOKEN,
                asset_type=MultiTokenAssetType(
                    asset_class=AssetClassEnum.MULTI_TOKEN,
                    contract=OriginatedAccountAddress("KT1EreNsT2gXRvuTUrpx6Ju4WMug5xcEpr43"),
                    token_id="1"
                ),
                asset_value=AssetValue(1)
            ),
            buy=AssetDescription(
                type=AssetClassEnum.FUNGIBLE_TOKEN,
                contract=None,
                token_id=None
            ),
            end_time=datetime(2022, 5, 2, 18, 20, 15, tzinfo=UTC),
            minimal_step=1,
            minimal_price=10,
            created_at=datetime(2022, 5, 2, 15, 33, 35, tzinfo=UTC),
            last_updated_at=datetime(2022, 5, 2, 15, 33, 35, tzinfo=UTC),
            buy_price=100000,
            status=AuctionStatusEnum.ACTIVE,
            ongoing=True,
            hash="1ed421e034a451d89ecb57f487595b28",
            start_at=datetime(2022, 5, 2, 15, 33, 35, tzinfo=UTC),
            auction_id="1ed421e034a451d89ecb57f487595b28",
            last_bid=AuctionBid(
                buyer=ImplicitAccountAddress('tz1Mxsc66En4HsVHr6rppYZW82ZpLhpupToC'),
                amount=AssetValue(1),
                date=datetime(2022, 5, 2, 16, 33, 35, tzinfo=UTC)
            ),
        )
