from abc import ABC
from abc import abstractmethod
from typing import final

from dipdup.datasources.tzkt.datasource import TzktDatasource
from dipdup.models import Transaction
from pydantic.dataclasses import dataclass

from rarible_marketplace_indexer.action.dto import CancelDto
from rarible_marketplace_indexer.action.dto import ListDto
from rarible_marketplace_indexer.models import Activity
from rarible_marketplace_indexer.models import ActivityTypeEnum
from rarible_marketplace_indexer.models import Order
from rarible_marketplace_indexer.models import StatusEnum
from rarible_marketplace_indexer.types.hen_marketplace.parameter.cancel_swap import CancelSwapParameter
from rarible_marketplace_indexer.types.hen_marketplace.storage import HenMarketplaceStorage


class ActionInterface(ABC):
    platform: str = NotImplemented

    @classmethod
    @abstractmethod
    async def handle(cls, transaction: Transaction, datasource: TzktDatasource):
        raise NotImplementedError


class AbstractListAction(ActionInterface):
    @staticmethod
    @abstractmethod
    def _get_list_dto(
        transaction: Transaction,
        datasource: TzktDatasource,
    ) -> ListDto:
        raise NotImplementedError

    @classmethod
    @final
    async def handle(
        cls,
        transaction: Transaction,
        datasource: TzktDatasource,
    ):
        dto = cls._get_list_dto(transaction, datasource)
        if not dto.started_at:
            dto.started_at = transaction.data.timestamp

        await Activity.create(
            type=ActivityTypeEnum.LIST,
            network=datasource.network,
            platform=cls.platform,
            internal_order_id=dto.internal_order_id,
            maker=dto.maker,
            contract=dto.contract,
            token_id=dto.token_id,
            amount=dto.amount,
            sell_price=dto.object_price,
            action_level=transaction.data.level,
            action_timestamp=transaction.data.timestamp,
        )

        await Order.create(
            network=datasource.network,
            platform=cls.platform,
            internal_order_id=dto.internal_order_id,
            status=StatusEnum.ACTIVE,
            started_at=dto.started_at,
            ended_at=None,
            cancelled=False,
            created_at=transaction.data.timestamp,
            last_updated_at=transaction.data.timestamp,
            make_price=dto.object_price,
            maker=dto.maker,
            make_contract=dto.contract,
            make_token_id=dto.token_id,
            make_amount=dto.amount,
        )


class AbstractCancelAction(ActionInterface):
    @staticmethod
    @abstractmethod
    def _get_cancel_dto(
        transaction: Transaction,
        datasource: TzktDatasource,
    ) -> CancelDto:
        raise NotImplementedError

    @classmethod
    @final
    async def handle(
        cls,
        transaction: Transaction[CancelSwapParameter, HenMarketplaceStorage],
        datasource: TzktDatasource,
    ):
        dto = cls._get_cancel_dto(transaction, datasource)

        last_list_activity = (
            await Activity.filter(
                network=datasource.network,
                platform=cls.platform,
                internal_order_id=dto.internal_order_id,
            )
            .order_by('-action_level')
            .first()
        )
        last_list_activity._custom_generated_pk = True
        cancel_activity = last_list_activity.clone()
        cancel_activity.action_level = transaction.data.level
        cancel_activity.action_timestamp = transaction.data.timestamp
        cancel_activity.type = ActivityTypeEnum.CANCEL
        await cancel_activity.save()

        order = (
            await Order.filter(
                network=datasource.network,
                platform=cls.platform,
                internal_order_id=dto.internal_order_id,
                status=StatusEnum.ACTIVE,
            )
            .order_by('-action_level')
            .first()
        )

        order.status = StatusEnum.CANCELLED
        order.cancelled = True
        order.ended_at = transaction.data.timestamp
        order.last_updated_at = transaction.data.timestamp

        await order.save()


@dataclass
class MatchDto:
    pass


class AbstractMatchAction(ActionInterface):
    @staticmethod
    @abstractmethod
    def _get_match_dto(
        transaction: Transaction,
        datasource: TzktDatasource,
    ) -> MatchDto:
        raise NotImplementedError

    @classmethod
    async def handle(
        cls,
        transaction: Transaction,
        datasource: TzktDatasource,
    ):
        internal_order_id = int(transaction.parameter.__root__)
        dto = cls._get_match_dto(transaction, datasource)

        last_list_activity = (
            await Activity.filter(
                network=datasource.network,
                platform=cls.platform,
                internal_order_id=internal_order_id,
            )
            .order_by('-action_level')
            .first()
        )
        last_list_activity._custom_generated_pk = True
        match_activity = last_list_activity.clone()
        match_activity.action_level = transaction.data.level
        match_activity.action_timestamp = transaction.data.timestamp
        match_activity.type = ActivityTypeEnum.MATCH
        await match_activity.save()

        order = await Order.get(
            network=datasource.network,
            platform=cls.platform,
            internal_order_id=internal_order_id,
        )
        order.fill = order.make_price
        order.status = StatusEnum.FILLED
        order.ended_at = transaction.data.timestamp
        order.last_updated_at = transaction.data.timestamp

        await order.save()
