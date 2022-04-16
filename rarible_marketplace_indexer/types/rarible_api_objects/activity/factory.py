from typing import Callable
from typing import Dict

from rarible_marketplace_indexer.models import Activity
from rarible_marketplace_indexer.models import ActivityTypeEnum
from rarible_marketplace_indexer.types.rarible_api_objects.activity.activity import RaribleApiActivity
from rarible_marketplace_indexer.types.rarible_api_objects.activity.activity import RaribleApiCancelActivity
from rarible_marketplace_indexer.types.rarible_api_objects.activity.activity import RaribleApiListActivity
from rarible_marketplace_indexer.types.rarible_api_objects.activity.activity import RaribleApiMatchActivity
from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset import Asset
from rarible_marketplace_indexer.types.tezos_objects.asset_value.xtz_value import Xtz
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress


class ActivityFactory:
    @classmethod
    def _build_list_activity(cls, activity: Activity) -> RaribleApiListActivity:
        return RaribleApiListActivity(
            id=activity.id,
            network=activity.network,
            hash=activity.operation_hash,
            maker=ImplicitAccountAddress(activity.maker),
            make=Asset.make_from_model(activity),
            take=Asset.take_from_model(activity),
            price=Xtz.from_u_tezos(activity.sell_price),
            source=activity.platform,
            date=activity.operation_timestamp,
        )

    @classmethod
    def _build_match_activity(cls, activity: Activity) -> RaribleApiMatchActivity:
        return RaribleApiMatchActivity(
            id=activity.id,
            network=activity.network,
            nft=Asset.make_from_model(activity),
            payment=Asset.take_from_model(activity),
            buyer=ImplicitAccountAddress(activity.taker),
            seller=ImplicitAccountAddress(activity.maker),
            price=Xtz.from_u_tezos(activity.sell_price),
            source=activity.platform,
            hash=activity.operation_hash,
            date=activity.operation_timestamp,
        )

    @classmethod
    def _build_cancel_activity(cls, activity: Activity) -> RaribleApiCancelActivity:
        return RaribleApiCancelActivity(
            id=activity.id,
            network=activity.network,
            maker=ImplicitAccountAddress(activity.maker),
            make=Asset.make_from_model(activity),
            take=Asset.take_from_model(activity),
            source=activity.platform,
            hash=activity.operation_hash,
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
