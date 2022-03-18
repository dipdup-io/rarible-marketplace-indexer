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
from rarible_marketplace_indexer.types.objkt_marketplace.parameter.ask import AskParameter
from rarible_marketplace_indexer.types.objkt_marketplace.parameter.fulfill_ask import FulfillAskParameter
from rarible_marketplace_indexer.types.objkt_marketplace.parameter.retract_ask import RetractAskParameter
from rarible_marketplace_indexer.types.objkt_marketplace.storage import ObjktMarketplaceStorage


class ObjktListAction(ListActionInterface):
    @staticmethod
    async def handle(
        transaction: Transaction[AskParameter, ObjktMarketplaceStorage],
        datasource: TzktDatasource,
    ):
        internal_order_id = int(transaction.storage.ask_id) - 1
        await Activity.create(
            type=ActivityTypeEnum.LIST,
            network=datasource.network,
            platform=PlatformEnum.OBJKT,
            internal_order_id=str(internal_order_id),
            maker=transaction.data.sender_address,
            contract=transaction.parameter.fa2,
            token_id=transaction.parameter.objkt_id,
            amount=transaction.parameter.amount,
            sell_price=transaction.parameter.price,
            action_level=transaction.data.level,
            action_timestamp=transaction.data.timestamp,
        )

        await Order.create(
            network=datasource.network,
            platform=PlatformEnum.OBJKT,
            internal_order_id=str(internal_order_id),
            status=StatusEnum.ACTIVE,
            started_at=transaction.data.timestamp,
            ended_at=None,
            cancelled=False,
            created_at=transaction.data.timestamp,
            last_updated_at=transaction.data.timestamp,
            maker=transaction.data.sender_address,
            make_contract=transaction.parameter.fa2,
            make_token_id=transaction.parameter.objkt_id,
            make_amount=transaction.parameter.amount,
        )


class ObjktCancelAction(ListActionInterface):
    @staticmethod
    async def handle(
        transaction: Transaction[RetractAskParameter, ObjktMarketplaceStorage],
        datasource: TzktDatasource,
    ):
        internal_order_id = int(transaction.parameter.__root__)

        list_activity = (
            await Activity.filter(
                network=datasource.network,
                platform=PlatformEnum.OBJKT,
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
            platform=PlatformEnum.OBJKT,
            internal_order_id=internal_order_id,
        )
        order.status = StatusEnum.CANCELLED
        order.cancelled = True
        order.ended_at = transaction.data.timestamp
        order.last_updated_at = transaction.data.timestamp

        await order.save()


class ObjktMatchAction(ListActionInterface):
    @staticmethod
    async def handle(
        transaction: Transaction[FulfillAskParameter, ObjktMarketplaceStorage],
        datasource: TzktDatasource,
    ):
        internal_order_id = int(transaction.parameter.__root__)

        list_activity = (
            await Activity.filter(
                network=datasource.network,
                platform=PlatformEnum.OBJKT,
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
            platform=PlatformEnum.OBJKT,
            internal_order_id=internal_order_id,
        )
        order.fill = order.make_price
        order.status = StatusEnum.FILLED
        order.ended_at = transaction.data.timestamp
        order.last_updated_at = transaction.data.timestamp

        await order.save()
