from datetime import datetime
from typing import Callable
from typing import Dict
from typing import Literal
from typing import Union

from humps import camelize
from pydantic import BaseModel

from rarible_marketplace_indexer.models import Activity
from rarible_marketplace_indexer.models import ActivityTypeEnum
from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.types.rarible_api_objects.asset_type import Asset
from rarible_marketplace_indexer.types.rarible_api_objects.asset_type import FungibleTokenAssetType
from rarible_marketplace_indexer.types.rarible_api_objects.asset_type import XtzAssetType
from rarible_marketplace_indexer.types.tezos_objects.tezos_currency import AssetValue
from rarible_marketplace_indexer.types.tezos_objects.tezos_currency import Xtz
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OperationHash


class AbstractRaribleApiActivity(BaseModel):
    type: str  # fixme
    source: PlatformEnum
    hash: OperationHash
    id: int
    date: datetime
    reverted: bool = False

    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True


class RaribleApiListActivity(AbstractRaribleApiActivity):
    type: Literal['LIST'] = 'LIST'  # fixme
    maker: ImplicitAccountAddress
    make: Asset
    take: Asset
    price: Xtz


class RaribleApiMatchActivity(AbstractRaribleApiActivity):
    type: Literal['SELL'] = 'SELL'  # fixme
    nft: Asset
    payment: Asset
    buyer: ImplicitAccountAddress
    seller: ImplicitAccountAddress
    price: Xtz


class RaribleApiCancelActivity(AbstractRaribleApiActivity):
    type: Literal['CANCEL_LIST'] = 'CANCEL_LIST'  # fixme
    maker: ImplicitAccountAddress
    make: Asset
    take: Asset


RaribleApiActivity = Union[RaribleApiListActivity, RaribleApiMatchActivity, RaribleApiCancelActivity]


class ActivityFactory:
    @classmethod
    def _build_list_activity(cls, activity: Activity) -> RaribleApiListActivity:
        return RaribleApiListActivity(
            hash=activity.operation_hash,
            maker=ImplicitAccountAddress(activity.maker),
            make=Asset(
                type=FungibleTokenAssetType(
                    contract=activity.contract,
                    token_id=activity.token_id,
                ),
                value=AssetValue(activity.amount),
            ),
            take=Asset(
                type=XtzAssetType(),
                value=Xtz.from_u_tezos(activity.sell_price),
            ),
            price=Xtz.from_u_tezos(activity.sell_price),
            source=activity.platform,
            id=activity.id,
            date=activity.operation_timestamp,
        )

    @classmethod
    def _build_match_activity(cls, activity: Activity) -> RaribleApiMatchActivity:
        return RaribleApiMatchActivity(
            nft=Asset(
                type=FungibleTokenAssetType(
                    contract=activity.contract,
                    token_id=activity.token_id,
                ),
                value=AssetValue(activity.amount),
            ),
            payment=Asset(
                type=XtzAssetType(),
                value=Xtz.from_u_tezos(activity.sell_price),
            ),
            buyer=ImplicitAccountAddress(activity.taker),
            seller=ImplicitAccountAddress(activity.maker),
            price=Xtz.from_u_tezos(activity.sell_price),
            source=activity.platform,
            hash=activity.operation_hash,
            id=activity.id,
            date=activity.operation_timestamp,
        )

    @classmethod
    def _build_cancel_activity(cls, activity: Activity) -> RaribleApiCancelActivity:
        return RaribleApiCancelActivity(
            maker=ImplicitAccountAddress(activity.maker),
            make=Asset(
                type=FungibleTokenAssetType(
                    contract=activity.contract,
                    token_id=activity.token_id,
                ),
                value=AssetValue(activity.amount),
            ),
            take=Asset(
                type=XtzAssetType(),
                value=Xtz.from_u_tezos(activity.sell_price),
            ),
            source=activity.platform,
            hash=activity.operation_hash,
            id=activity.id,
            date=activity.operation_timestamp,
        )

    @classmethod
    def _get_factory_method(cls, activity: Activity) -> callable:
        method_map: Dict[ActivityTypeEnum, Callable[[Activity], callable]] = {
            ActivityTypeEnum.LIST: cls._build_list_activity,
            ActivityTypeEnum.MATCH: cls._build_match_activity,
            ActivityTypeEnum.CANCEL: cls._build_cancel_activity,
        }

        return method_map.get(activity.type, cls._build_list_activity)

    @classmethod
    def build(cls, activity: Activity) -> RaribleApiActivity:
        factory_method = cls._get_factory_method(activity)

        return factory_method(activity)
