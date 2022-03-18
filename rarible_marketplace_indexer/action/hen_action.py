from dipdup.datasources.tzkt.datasource import TzktDatasource
from dipdup.models import Transaction

from rarible_marketplace_indexer.action.action import ListActionInterface
from rarible_marketplace_indexer.models import Activity
from rarible_marketplace_indexer.models import ActivityTypeEnum
from rarible_marketplace_indexer.models import Order
from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.models import StatusEnum
from rarible_marketplace_indexer.types.hen_marketplace.parameter.cancel_swap import CancelSwapParameter
from rarible_marketplace_indexer.types.hen_marketplace.parameter.collect import CollectParameter
from rarible_marketplace_indexer.types.hen_marketplace.parameter.swap import SwapParameter
from rarible_marketplace_indexer.types.hen_marketplace.storage import HenMarketplaceStorage


class HENListAction(ListActionInterface):
    @staticmethod
    async def handle(
        transaction: Transaction[SwapParameter, HenMarketplaceStorage],
        datasource: TzktDatasource,
    ):
        internal_order_id = int(transaction.storage.counter) - 1
        await Activity.create(
            type=ActivityTypeEnum.LIST,
            network=datasource.network,
            platform=PlatformEnum.HEN,
            internal_order_id=str(internal_order_id),
            maker=transaction.data.sender_address,
            contract=transaction.storage.objkt,
            token_id=transaction.parameter.objkt_id,
            amount=transaction.parameter.objkt_amount,
            sell_price=transaction.parameter.xtz_per_objkt,
            action_level=transaction.data.level,
            action_timestamp=transaction.data.timestamp,
        )

        await Order.create(
            network=datasource.network,
            platform=PlatformEnum.HEN,
            internal_order_id=str(internal_order_id),
            status=StatusEnum.ACTIVE,
            started_at=transaction.data.timestamp,
            ended_at=None,
            cancelled=False,
            created_at=transaction.data.timestamp,
            last_updated_at=transaction.data.timestamp,
            make_price=transaction.parameter.xtz_per_objkt,
            maker=transaction.data.sender_address,
            make_contract=transaction.storage.objkt,
            make_token_id=transaction.parameter.objkt_id,
            make_amount=transaction.parameter.objkt_amount,
        )


class HENCancelAction(ListActionInterface):
    @staticmethod
    async def handle(
        transaction: Transaction[CancelSwapParameter, HenMarketplaceStorage],
        datasource: TzktDatasource,
    ):
        internal_order_id = int(transaction.parameter.__root__)

        list_activity = (
            await Activity.filter(
                network=datasource.network,
                platform=PlatformEnum.HEN,
                internal_order_id=internal_order_id,
            )
            .order_by('-action_level')
            .first()
        )
        list_activity._custom_generated_pk = True
        cancel_activity = list_activity.clone()
        cancel_activity.action_level = transaction.data.level
        cancel_activity.action_timestamp = transaction.data.timestamp
        cancel_activity.type = ActivityTypeEnum.CANCEL
        await cancel_activity.save()

        order = await Order.get(
            network=datasource.network,
            platform=PlatformEnum.HEN,
            internal_order_id=internal_order_id,
        )
        order.status = StatusEnum.CANCELLED
        order.cancelled = True
        order.ended_at = transaction.data.timestamp
        order.last_updated_at = transaction.data.timestamp

        await order.save()


class HENMatchAction(ListActionInterface):
    @staticmethod
    async def handle(
        transaction: Transaction[CollectParameter, HenMarketplaceStorage],
        datasource: TzktDatasource,
    ):
        internal_order_id = int(transaction.parameter.__root__)

        list_activity = (
            await Activity.filter(
                network=datasource.network,
                platform=PlatformEnum.HEN,
                internal_order_id=internal_order_id,
            )
            .order_by('-action_level')
            .first()
        )
        list_activity._custom_generated_pk = True
        cancel_activity = list_activity.clone()
        cancel_activity.action_level = transaction.data.level
        cancel_activity.action_timestamp = transaction.data.timestamp
        cancel_activity.type = ActivityTypeEnum.MATCH
        await cancel_activity.save()

        order = await Order.get(
            network=datasource.network,
            platform=PlatformEnum.HEN,
            internal_order_id=internal_order_id,
        )
        order.fill = order.make_price
        order.status = StatusEnum.FILLED
        order.ended_at = transaction.data.timestamp
        order.last_updated_at = transaction.data.timestamp

        await order.save()
