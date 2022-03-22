from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from rarible_marketplace_indexer.models import Order
from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.models import StatusEnum
from rarible_marketplace_indexer.types.rarible_api_objects.asset_type import Asset
from rarible_marketplace_indexer.types.rarible_api_objects.asset_type import AssetClassEnum
from rarible_marketplace_indexer.types.rarible_api_objects.asset_type import CryptoPunksAssetType
from rarible_marketplace_indexer.types.rarible_api_objects.asset_type import XtzAssetType
from rarible_marketplace_indexer.types.tezos_objects.tezos_currency import AssetValue
from rarible_marketplace_indexer.types.tezos_objects.tezos_currency import Xtz
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress


class RaribleApiOrder(BaseModel):
    id: str
    fill: Xtz
    platform: PlatformEnum
    status: StatusEnum
    started_at: datetime
    ended_at: Optional[datetime]
    make_stock: AssetValue
    created_at: datetime
    last_updated_at: datetime
    make_price: Xtz
    maker: ImplicitAccountAddress
    make: Asset
    take: Asset


class OrderFactory:
    @staticmethod
    def build(order: Order) -> RaribleApiOrder:
        return RaribleApiOrder(
            id=f'tezos_{order.network}:{order.id}',
            fill=order.fill,
            platform=order.platform,
            status=order.status,
            started_at=order.started_at,
            ended_at=order.ended_at,
            make_stock=order.make_stock,
            created_at=order.created_at,
            last_updated_at=order.last_updated_at,
            make_price=order.make_price,
            maker=order.maker,
            make=Asset(
                type=CryptoPunksAssetType(
                    asset_class=AssetClassEnum.CRYPTO_PUNKS, contract=order.make_contract, token_id=order.make_token_id
                ),
                value=order.make_value,
            ),
            take=Asset(
                type=XtzAssetType(
                    asset_class=AssetClassEnum.XTZ,
                ),
                value=order.make_price,
            ),
        )
