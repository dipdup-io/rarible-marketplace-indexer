from abc import ABC
from abc import abstractmethod
from typing import final

from dipdup.datasources.tzkt.datasource import TzktDatasource
from dipdup.models import Transaction

from rarible_marketplace_indexer.action.dto import CancelDto
from rarible_marketplace_indexer.action.dto import ListDto
from rarible_marketplace_indexer.action.dto import MatchDto
from rarible_marketplace_indexer.models import Activity
from rarible_marketplace_indexer.models import ActivityTypeEnum
from rarible_marketplace_indexer.models import Order
from rarible_marketplace_indexer.models import StatusEnum
from rarible_marketplace_indexer.types.tezos_objects.tezos_currency import Xtz


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
            operation_level=transaction.data.level,
            operation_timestamp=transaction.data.timestamp,
            operation_hash=transaction.data.hash,
        )

        await Order.create(
            network=datasource.network,
            platform=cls.platform,
            internal_order_id=dto.internal_order_id,
            status=StatusEnum.ACTIVE,
            started_at=dto.started_at,
            ended_at=None,
            make_stock=dto.amount,
            created_at=transaction.data.timestamp,
            last_updated_at=transaction.data.timestamp,
            make_price=dto.object_price,
            maker=dto.maker,
            make_contract=dto.contract,
            make_token_id=dto.token_id,
            make_value=dto.amount,
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
        transaction: Transaction,
        datasource: TzktDatasource,
    ):
        dto = cls._get_cancel_dto(transaction, datasource)

        last_order_activity = (
            await Activity.filter(
                network=datasource.network,
                platform=cls.platform,
                internal_order_id=dto.internal_order_id,
            )
            .order_by('-operation_level')
            .first()
        )
        last_order_activity._custom_generated_pk = False
        cancel_activity = last_order_activity.clone()

        cancel_activity.operation_level = transaction.data.level
        cancel_activity.operation_timestamp = transaction.data.timestamp
        cancel_activity.operation_hash = transaction.data.hash

        cancel_activity.type = ActivityTypeEnum.CANCEL
        await cancel_activity.save()

        order = (
            await Order.filter(
                network=datasource.network,
                platform=cls.platform,
                internal_order_id=dto.internal_order_id,
                status=StatusEnum.ACTIVE,
            )
            .order_by('-id')
            .first()
        )

        order.status = StatusEnum.CANCELLED
        order.cancelled = True
        order.ended_at = transaction.data.timestamp
        order.last_updated_at = transaction.data.timestamp

        await order.save()


class AbstractMatchAction(ActionInterface):
    @staticmethod
    @abstractmethod
    def _get_match_dto(
        transaction: Transaction,
        datasource: TzktDatasource,
    ) -> MatchDto:
        raise NotImplementedError

    @staticmethod
    @final
    def _process_order_match(order: Order, dto: MatchDto) -> Order:
        order.make_stock -= dto.match_amount
        order.fill = Xtz(order.fill) + (Xtz(order.make_price) * dto.match_amount)

        if order.make_stock <= 0:
            order.status = StatusEnum.FILLED
            order.ended_at = dto.match_timestamp

        return order

    @classmethod
    async def handle(
        cls,
        transaction: Transaction,
        datasource: TzktDatasource,
    ):
        dto = cls._get_match_dto(transaction, datasource)

        last_list_activity = (
            await Activity.filter(
                network=datasource.network,
                platform=cls.platform,
                internal_order_id=dto.internal_order_id,
            )
            .order_by('-operation_level')
            .first()
        )
        last_list_activity._custom_generated_pk = False
        match_activity = last_list_activity.clone()

        match_activity.operation_level = transaction.data.level
        match_activity.operation_timestamp = transaction.data.timestamp
        match_activity.operation_hash = transaction.data.hash

        match_activity.type = ActivityTypeEnum.MATCH
        match_activity.amount = dto.match_amount
        await match_activity.save()

        order = await Order.get(
            network=datasource.network,
            platform=cls.platform,
            internal_order_id=dto.internal_order_id,
            status=StatusEnum.ACTIVE,
        )
        order.last_updated_at = transaction.data.timestamp
        order = cls._process_order_match(order, dto)

        await order.save()
