from typing import Callable
from typing import Dict

from rarible_marketplace_indexer.models import ActivityModel
from rarible_marketplace_indexer.models import ActivityTypeEnum
from rarible_marketplace_indexer.types.rarible_api_objects.activity.order.activity import RaribleApiOrderActivity
from rarible_marketplace_indexer.types.rarible_api_objects.activity.order.activity import RaribleApiOrderCancelActivity
from rarible_marketplace_indexer.types.rarible_api_objects.activity.order.activity import RaribleApiOrderListActivity
from rarible_marketplace_indexer.types.rarible_api_objects.activity.order.activity import RaribleApiOrderMatchActivity
from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset import Asset
from rarible_marketplace_indexer.types.tezos_objects.asset_value.xtz_value import Xtz
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress


class RaribleApiOrderActivityFactory:
    @classmethod
    def _build_list_activity(cls, activity: ActivityModel) -> RaribleApiOrderListActivity:
        return RaribleApiOrderListActivity(
            id=activity.id,
            order_id=activity.order_id,
            network=activity.network,
            hash=activity.operation_hash,
            maker=ImplicitAccountAddress(activity.maker),
            make=Asset.make_from_model(activity),
            take=Asset.take_from_model(activity),
            price=Xtz(activity.sell_price),
            source=activity.platform,
            date=activity.operation_timestamp,
        )

    @classmethod
    def _build_match_activity(cls, activity: ActivityModel) -> RaribleApiOrderMatchActivity:
        return RaribleApiOrderMatchActivity(
            id=activity.id,
            order_id=activity.order_id,
            network=activity.network,
            nft=Asset.make_from_model(activity),
            payment=Asset.take_from_model(activity),
            buyer=ImplicitAccountAddress(activity.taker),
            seller=ImplicitAccountAddress(activity.maker),
            price=Xtz(activity.sell_price),
            source=activity.platform,
            hash=activity.operation_hash,
            date=activity.operation_timestamp,
        )

    @classmethod
    def _build_cancel_activity(cls, activity: ActivityModel) -> RaribleApiOrderCancelActivity:
        return RaribleApiOrderCancelActivity(
            id=activity.id,
            order_id=activity.order_id,
            network=activity.network,
            maker=ImplicitAccountAddress(activity.maker),
            make=Asset.make_from_model(activity),
            take=Asset.take_from_model(activity),
            source=activity.platform,
            hash=activity.operation_hash,
            date=activity.operation_timestamp,
        )

    @classmethod
    def _get_factory_method(cls, activity: ActivityModel) -> callable:
        method_map: Dict[ActivityTypeEnum, Callable[[ActivityModel], callable]] = {
            ActivityTypeEnum.ORDER_LIST: cls._build_list_activity,
            ActivityTypeEnum.ORDER_MATCH: cls._build_match_activity,
            ActivityTypeEnum.ORDER_CANCEL: cls._build_cancel_activity,
        }

        return method_map.get(activity.type, cls._build_list_activity)

    @classmethod
    def build(cls, activity: ActivityModel) -> RaribleApiOrderActivity:
        factory_method = cls._get_factory_method(activity)

        return factory_method(activity)
