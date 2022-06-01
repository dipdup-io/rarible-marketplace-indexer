from abc import ABC
from abc import abstractmethod
from typing import final

from dipdup.datasources.tzkt.datasource import TzktDatasource
from dipdup.models import Transaction

from rarible_marketplace_indexer.event.dto import CancelDto
from rarible_marketplace_indexer.event.dto import ListDto
from rarible_marketplace_indexer.event.dto import MatchDto
from rarible_marketplace_indexer.models import ActivityModel
from rarible_marketplace_indexer.models import ActivityTypeEnum
from rarible_marketplace_indexer.models import OrderModel
from rarible_marketplace_indexer.models import OrderStatusEnum
from rarible_marketplace_indexer.types.tezos_objects.asset_value.asset_value import AssetValue


class EventInterface(ABC):
    platform: str = NotImplemented

    @classmethod
    @abstractmethod
    async def handle(cls, transaction: Transaction, datasource: TzktDatasource):
        raise NotImplementedError


class AbstractOrderListEvent(EventInterface):
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

        order = await OrderModel.create(
            network=datasource.network,
            platform=cls.platform,
            internal_order_id=dto.internal_order_id,
            status=OrderStatusEnum.ACTIVE,
            started_at=dto.started_at,
            ended_at=dto.ended_at,
            make_stock=dto.make.value,
            salt=transaction.data.counter,
            created_at=transaction.data.timestamp,
            last_updated_at=transaction.data.timestamp,
            make_price=dto.make_price,
            maker=dto.maker,
            make_asset_class=dto.make.asset_class,
            make_contract=dto.make.contract,
            make_token_id=dto.make.token_id,
            make_value=dto.make.value,
            take_asset_class=dto.take.asset_class,
            take_contract=dto.take.contract,
            take_token_id=dto.take.token_id,
            take_value=dto.take.value,
        )

        await ActivityModel.create(
            type=ActivityTypeEnum.ORDER_LIST,
            network=datasource.network,
            platform=cls.platform,
            order_id=order.id,
            internal_order_id=dto.internal_order_id,
            maker=dto.maker,
            make_asset_class=dto.make.asset_class,
            make_contract=dto.make.contract,
            make_token_id=dto.make.token_id,
            make_value=dto.make.value,
            take_asset_class=dto.take.asset_class,
            take_contract=dto.take.contract,
            take_token_id=dto.take.token_id,
            take_value=dto.take.value,
            sell_price=dto.make_price,
            operation_level=transaction.data.level,
            operation_timestamp=transaction.data.timestamp,
            operation_hash=transaction.data.hash,
            operation_counter=transaction.data.counter,
            operation_nonce=transaction.data.nonce,
        )


class AbstractOrderCancelEvent(EventInterface):
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
            await ActivityModel.filter(
                network=datasource.network,
                platform=cls.platform,
                internal_order_id=dto.internal_order_id,
            )
            .order_by('-operation_level')
            .first()
        )
        cancel_activity = last_order_activity.apply(transaction)

        cancel_activity.type = ActivityTypeEnum.ORDER_CANCEL
        await cancel_activity.save()

        order = (
            await OrderModel.filter(
                network=datasource.network,
                platform=cls.platform,
                internal_order_id=dto.internal_order_id,
                status=OrderStatusEnum.ACTIVE,
            )
            .order_by('-id')
            .first()
        )

        order.status = OrderStatusEnum.CANCELLED
        order.cancelled = True
        order.ended_at = transaction.data.timestamp
        order.last_updated_at = transaction.data.timestamp

        await order.save()


class AbstractOrderMatchEvent(EventInterface):
    @staticmethod
    @abstractmethod
    def _get_match_dto(
        transaction: Transaction,
        datasource: TzktDatasource,
    ) -> MatchDto:
        raise NotImplementedError

    @staticmethod
    @final
    def _process_order_match(order: OrderModel, dto: MatchDto) -> OrderModel:
        order.make_stock -= dto.match_amount
        order.fill += dto.match_amount

        if order.make_stock <= 0:
            order.status = OrderStatusEnum.FILLED
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
            await ActivityModel.filter(
                network=datasource.network,
                platform=cls.platform,
                internal_order_id=dto.internal_order_id,
            )
            .order_by('-operation_level')
            .first()
        )
        match_activity = last_list_activity.apply(transaction)

        match_activity.type = ActivityTypeEnum.ORDER_MATCH
        match_activity.taker = transaction.data.sender_address

        match_activity.make_value = dto.match_amount
        match_activity.take_value = AssetValue(match_activity.sell_price * dto.match_amount)

        await match_activity.save()

        order = await OrderModel.get(
            network=datasource.network,
            platform=cls.platform,
            internal_order_id=dto.internal_order_id,
            status=OrderStatusEnum.ACTIVE,
        )
        order.last_updated_at = transaction.data.timestamp
        order = cls._process_order_match(order, dto)

        await order.save()


class AbstractPutBidEvent(EventInterface):
    @staticmethod
    @abstractmethod
    def _get_bid_dto(
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
        dto = cls._get_bid_dto(transaction, datasource)

        order = await OrderModel.get_or_none(
            internal_order_id=dto.internal_order_id, network=datasource.network, platform=cls.platform, status=OrderStatusEnum.ACTIVE
        )

        if order is None:
            order = await OrderModel.create(
                network=datasource.network,
                platform=cls.platform,
                internal_order_id=dto.internal_order_id,
                status=OrderStatusEnum.ACTIVE,
                started_at=transaction.data.timestamp,
                ended_at=dto.ended_at,
                make_stock=dto.make.value,
                salt=transaction.data.counter,
                created_at=transaction.data.timestamp,
                last_updated_at=transaction.data.timestamp,
                make_price=dto.make_price,
                maker=dto.maker,
                make_asset_class=dto.make.asset_class,
                make_contract=dto.make.contract,
                make_token_id=dto.make.token_id,
                make_value=dto.make.value,
                take_asset_class=dto.take.asset_class,
                take_contract=dto.take.contract,
                take_token_id=dto.take.token_id,
                take_value=dto.take.value,
            )
        else:
            order.last_updated_at = transaction.data.timestamp
            order.make_value = dto.make.value
            order.take_value = dto.take.value
            order.save()

        await ActivityModel.create(
            type=ActivityTypeEnum.MAKE_BID,
            network=datasource.network,
            platform=cls.platform,
            order_id=order.id,
            internal_order_id=dto.internal_order_id,
            maker=dto.maker,
            make_asset_class=dto.make.asset_class,
            make_contract=dto.make.contract,
            make_token_id=dto.make.token_id,
            make_value=dto.make.value,
            take_asset_class=dto.take.asset_class,
            take_contract=dto.take.contract,
            take_token_id=dto.take.token_id,
            take_value=dto.take.value,
            sell_price=dto.make_price,
            operation_level=transaction.data.level,
            operation_timestamp=transaction.data.timestamp,
            operation_hash=transaction.data.hash,
            operation_counter=transaction.data.counter,
            operation_nonce=transaction.data.nonce,
        )


class AbstractPutFloorBidEvent(EventInterface):
    @staticmethod
    @abstractmethod
    def _get_floor_bid_dto(
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
        dto = cls._get_floor_bid_dto(transaction, datasource)

        order = await OrderModel.get_or_none(
            internal_order_id=dto.internal_order_id, network=datasource.network, platform=cls.platform, status=OrderStatusEnum.ACTIVE
        )

        if order is None:
            order = await OrderModel.create(
                network=datasource.network,
                platform=cls.platform,
                internal_order_id=dto.internal_order_id,
                status=OrderStatusEnum.ACTIVE,
                started_at=transaction.data.timestamp,
                ended_at=dto.ended_at,
                make_stock=dto.make.value,
                salt=transaction.data.counter,
                created_at=transaction.data.timestamp,
                last_updated_at=transaction.data.timestamp,
                make_price=dto.make_price,
                maker=dto.maker,
                make_asset_class=dto.make.asset_class,
                make_contract=dto.make.contract,
                make_token_id=dto.make.token_id,
                make_value=dto.make.value,
                take_asset_class=dto.take.asset_class,
                take_contract=dto.take.contract,
                take_token_id=dto.take.token_id,
                take_value=dto.take.value,
            )
        else:
            order.last_updated_at = transaction.data.timestamp
            order.make_value = dto.make.value
            order.take_value = dto.take_price
            order.save()

        await ActivityModel.create(
            type=ActivityTypeEnum.MAKE_FLOOR_BID,
            network=datasource.network,
            platform=cls.platform,
            order_id=order.id,
            internal_order_id=dto.internal_order_id,
            maker=dto.maker,
            make_asset_class=dto.make.asset_class,
            make_contract=dto.make.contract,
            make_token_id=dto.make.token_id,
            make_value=dto.make.value,
            take_asset_class=dto.take.asset_class,
            take_contract=dto.take.contract,
            take_token_id=dto.take.token_id,
            take_value=dto.take.value,
            sell_price=dto.make_price,
            operation_level=transaction.data.level,
            operation_timestamp=transaction.data.timestamp,
            operation_hash=transaction.data.hash,
            operation_counter=transaction.data.counter,
            operation_nonce=transaction.data.nonce,
        )


class AbstractAcceptBidEvent(EventInterface):
    @staticmethod
    @abstractmethod
    def _get_accept_bid_dto(
        transaction: Transaction,
        datasource: TzktDatasource,
    ) -> MatchDto:
        raise NotImplementedError

    @staticmethod
    @final
    def _process_bid_match(order: OrderModel, dto: MatchDto) -> OrderModel:
        order.status = OrderStatusEnum.FILLED
        order.ended_at = dto.match_timestamp
        return order

    @classmethod
    async def handle(
        cls,
        transaction: Transaction,
        datasource: TzktDatasource,
    ):
        dto = cls._get_accept_bid_dto(transaction, datasource)

        last_list_activity = (
            await ActivityModel.filter(
                network=datasource.network,
                platform=cls.platform,
                internal_order_id=dto.internal_order_id,
            )
            .order_by('-operation_level')
            .first()
        )
        match_activity = last_list_activity.apply(transaction)

        match_activity.type = ActivityTypeEnum.GET_BID
        match_activity.taker = transaction.data.sender_address

        await match_activity.save()

        order = await OrderModel.get(
            network=datasource.network,
            platform=cls.platform,
            internal_order_id=dto.internal_order_id,
            status=OrderStatusEnum.ACTIVE,
        )
        order.last_updated_at = transaction.data.timestamp
        order = cls._process_bid_match(order, dto)

        await order.save()


class AbstractAcceptFloorBidEvent(EventInterface):
    @staticmethod
    @abstractmethod
    def _get_accept_floor_bid_dto(
        transaction: Transaction,
        datasource: TzktDatasource,
    ) -> MatchDto:
        raise NotImplementedError

    @staticmethod
    @final
    def _process_floor_bid_match(order: OrderModel, dto: MatchDto) -> OrderModel:
        order.status = OrderStatusEnum.FILLED
        order.ended_at = dto.match_timestamp
        return order

    @classmethod
    async def handle(
        cls,
        transaction: Transaction,
        datasource: TzktDatasource,
    ):
        dto = cls._get_accept_floor_bid_dto(transaction, datasource)

        last_list_activity = (
            await ActivityModel.filter(
                network=datasource.network,
                platform=cls.platform,
                internal_order_id=dto.internal_order_id,
            )
            .order_by('-operation_level')
            .first()
        )
        match_activity = last_list_activity.apply(transaction)

        match_activity.type = ActivityTypeEnum.GET_FLOOR_BID
        match_activity.taker = transaction.data.sender_address

        match_activity.take_token_id = dto.token_id
        await match_activity.save()

        order = await OrderModel.get(
            network=datasource.network,
            platform=cls.platform,
            internal_order_id=dto.internal_order_id,
            status=OrderStatusEnum.ACTIVE,
        )
        order.last_updated_at = transaction.data.timestamp
        order = cls._process_floor_bid_match(order, dto)

        await order.save()


class AbstractBidCancelEvent(EventInterface):
    @staticmethod
    @abstractmethod
    def _get_cancel_bid_dto(
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
        dto = cls._get_cancel_bid_dto(transaction, datasource)
        last_bid_activity = (
            await ActivityModel.filter(
                network=datasource.network,
                platform=cls.platform,
                internal_order_id=dto.internal_order_id,
            )
            .order_by('-operation_level')
            .first()
        )
        cancel_activity = last_bid_activity.apply(transaction)

        cancel_activity.type = ActivityTypeEnum.CANCEL_BID
        await cancel_activity.save()

        bid = (
            await OrderModel.filter(
                network=datasource.network,
                platform=cls.platform,
                internal_order_id=dto.internal_order_id,
                status=OrderStatusEnum.ACTIVE,
            )
            .order_by('-id')
            .first()
        )

        bid.status = OrderStatusEnum.CANCELLED
        bid.ended_at = transaction.data.timestamp
        bid.last_updated_at = transaction.data.timestamp

        await bid.save()


class AbstractFloorBidCancelEvent(EventInterface):
    @staticmethod
    @abstractmethod
    def _get_cancel_floor_bid_dto(
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
        dto = cls._get_cancel_floor_bid_dto(transaction, datasource)
        last_bid_activity = (
            await ActivityModel.filter(
                network=datasource.network,
                platform=cls.platform,
                internal_order_id=dto.internal_order_id,
            )
            .order_by('-operation_level')
            .first()
        )
        cancel_activity = last_bid_activity.apply(transaction)

        cancel_activity.type = ActivityTypeEnum.CANCEL_FLOOR_BID
        await cancel_activity.save()

        bid = (
            await OrderModel.filter(
                network=datasource.network,
                platform=cls.platform,
                internal_order_id=dto.internal_order_id,
                status=OrderStatusEnum.ACTIVE,
            )
            .order_by('-id')
            .first()
        )

        bid.status = OrderStatusEnum.CANCELLED
        bid.ended_at = transaction.data.timestamp
        bid.last_updated_at = transaction.data.timestamp

        await bid.save()
