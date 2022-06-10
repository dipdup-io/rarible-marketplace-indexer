from abc import ABC
from abc import abstractmethod
from datetime import timedelta
from typing import final

from dipdup.datasources.tzkt.datasource import TzktDatasource
from dipdup.models import Transaction

from rarible_marketplace_indexer.event.dto import CancelDto
from rarible_marketplace_indexer.event.dto import FinishAuctionDto
from rarible_marketplace_indexer.event.dto import ListDto
from rarible_marketplace_indexer.event.dto import MatchDto
from rarible_marketplace_indexer.event.dto import PutAuctionBidDto
from rarible_marketplace_indexer.event.dto import StartAuctionDto
from rarible_marketplace_indexer.models import ActivityModel
from rarible_marketplace_indexer.models import ActivityTypeEnum
from rarible_marketplace_indexer.models import AuctionActivityModel
from rarible_marketplace_indexer.models import AuctionModel
from rarible_marketplace_indexer.models import AuctionStatusEnum
from rarible_marketplace_indexer.models import OrderModel
from rarible_marketplace_indexer.models import OrderStatusEnum
from rarible_marketplace_indexer.types.rarible_api_objects.asset.enum import AssetClassEnum
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
        if not dto.start_at:
            dto.start_at = transaction.data.timestamp

        order = await OrderModel.create(
            network=datasource.network,
            platform=cls.platform,
            internal_order_id=dto.internal_order_id,
            status=OrderStatusEnum.ACTIVE,
            start_at=dto.start_at,
            end_at=dto.end_at,
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

        if dto.end_at is None:
            dto.end_at = dto.start_at + timedelta(weeks=1)

        order = await OrderModel.get_or_none(
            internal_order_id=dto.internal_order_id, network=datasource.network, platform=cls.platform, status=OrderStatusEnum.ACTIVE
        )

        if order is None:
            order = await OrderModel.create(
                network=datasource.network,
                platform=cls.platform,
                internal_order_id=dto.internal_order_id,
                status=OrderStatusEnum.ACTIVE,
                start_at=dto.start_at,
                end_at=dto.end_at,
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

        if dto.end_at is None:
            dto.end_at = dto.start_at + timedelta(weeks=1)

        order = await OrderModel.get_or_none(
            internal_order_id=dto.internal_order_id, network=datasource.network, platform=cls.platform, status=OrderStatusEnum.ACTIVE
        )

        if order is None:
            order = await OrderModel.create(
                network=datasource.network,
                platform=cls.platform,
                internal_order_id=dto.internal_order_id,
                status=OrderStatusEnum.ACTIVE,
                start_at=dto.start_at,
                end_at=dto.end_at,
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
        order.taker = transaction.data.sender_address
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
        order.taker = transaction.data.sender_address
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

        cancel_activity.type = ActivityTypeEnum.CANCEL_BID
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


class AbstractStartAuctionEvent(EventInterface):
    @staticmethod
    @abstractmethod
    def _get_start_auction_dto(
        transaction: Transaction,
        datasource: TzktDatasource,
    ) -> StartAuctionDto:
        raise NotImplementedError

    @classmethod
    @final
    async def handle(
        cls,
        transaction: Transaction,
        datasource: TzktDatasource,
    ):
        dto = cls._get_start_auction_dto(transaction, datasource)
        order_status = AuctionStatusEnum.INACTIVE
        ongoing = False
        if dto.start_at == transaction.data.timestamp:
            order_status = AuctionStatusEnum.ACTIVE
            ongoing = True

        auction = await AuctionModel.create(
            network=datasource.network,
            platform=cls.platform,
            auction_id=dto.auction_id,
            status=order_status,
            start_at=dto.start_at,
            ended_at=None,
            created_at=transaction.data.timestamp,
            end_time=dto.start_at + timedelta(seconds=dto.duration),
            last_updated_at=transaction.data.timestamp,
            ongoing=ongoing,
            seller=transaction.data.sender_address,
            sell_asset_class=AssetClassEnum.MULTI_TOKEN,
            sell_contract=dto.sell_contract,
            sell_token_id=dto.sell_token_id,
            sell_value=dto.sell_value,
            buy_asset_class=AssetClassEnum.FUNGIBLE_TOKEN,
            buy_contract=dto.buy_asset.contract,
            buy_token_id=dto.buy_asset.token_id,
            minimal_step=dto.min_step,
            minimal_price=dto.min_price,
            duration=dto.duration,
            buy_price=dto.buy_price,
            max_seller_fees=dto.max_seller_fees,
            last_bid_amount=None,
            last_bid_bidder=None,
            last_bid_date=None,
        )

        await AuctionActivityModel.create(
            auction_id=auction.id,
            type=ActivityTypeEnum.AUCTION_CREATED,
            network=datasource.network,
            platform=cls.platform,
            internal_auction_id=dto.auction_id,
            bid_value=None,
            bid_bidder=None,
            date=transaction.data.timestamp,
            last_updated_at=transaction.data.timestamp,
            operation_level=transaction.data.level,
            operation_timestamp=transaction.data.timestamp,
            operation_hash=transaction.data.hash,
            operation_counter=transaction.data.counter,
            operation_nonce=transaction.data.nonce,
        )

        if ongoing:
            await AuctionActivityModel.create(
                auction_id=auction.id,
                type=ActivityTypeEnum.AUCTION_STARTED,
                network=datasource.network,
                platform=cls.platform,
                internal_auction_id=dto.auction_id,
                bid_value=None,
                bid_bidder=None,
                date=transaction.data.timestamp,
                last_updated_at=transaction.data.timestamp,
                operation_level=transaction.data.level,
                operation_timestamp=transaction.data.timestamp,
                operation_hash=transaction.data.hash,
                operation_counter=transaction.data.counter,
                operation_nonce=transaction.data.nonce,
            )


class AbstractPutAuctionBidEvent(EventInterface):
    @staticmethod
    @abstractmethod
    def _get_put_auction_bid_dto(
        transaction: Transaction,
        datasource: TzktDatasource,
    ) -> PutAuctionBidDto:
        raise NotImplementedError

    @classmethod
    @final
    async def handle(
        cls,
        transaction: Transaction,
        datasource: TzktDatasource,
    ):
        dto = cls._get_put_auction_bid_dto(transaction, datasource)

        auction = (
            await AuctionModel.filter(
                network=datasource.network,
                platform=cls.platform,
                auction_id=dto.auction_id,
            )
            .order_by('-id')
            .first()
        )

        auction.last_updated_at = transaction.data.timestamp
        auction.last_bid_date = transaction.data.timestamp
        auction.last_bid_amount = dto.bid_value
        auction.last_bid_bidder = dto.bidder
        if dto.bid_value >= auction.buy_price:
            auction.status = AuctionStatusEnum.FINISHED
            auction.ongoing = False
            auction.ended_at = transaction.data.timestamp
            auction.save()

            await AuctionActivityModel.create(
                auction_id=auction.id,
                type=ActivityTypeEnum.AUCTION_FINISHED,
                network=datasource.network,
                platform=cls.platform,
                internal_auction_id=dto.auction_id,
                bid_value=dto.bid_value,
                bid_bidder=dto.bidder,
                date=transaction.data.timestamp,
                last_updated_at=transaction.data.timestamp,
                operation_level=transaction.data.level,
                operation_timestamp=transaction.data.timestamp,
                operation_hash=transaction.data.hash,
                operation_counter=transaction.data.counter,
                operation_nonce=transaction.data.nonce,
            )
        else:
            auction.status = AuctionStatusEnum.ACTIVE
            auction.ongoing = True
            auction.save()

            await AuctionActivityModel.create(
                auction_id=auction.id,
                type=ActivityTypeEnum.AUCTION_BID,
                network=datasource.network,
                platform=cls.platform,
                internal_auction_id=dto.auction_id,
                bid_value=dto.bid_value,
                bid_bidder=dto.bidder,
                date=transaction.data.timestamp,
                last_updated_at=transaction.data.timestamp,
                operation_level=transaction.data.level,
                operation_timestamp=transaction.data.timestamp,
                operation_hash=transaction.data.hash,
                operation_counter=transaction.data.counter,
                operation_nonce=transaction.data.nonce,
            )


class AbstractFinishAuctionEvent(EventInterface):
    @staticmethod
    @abstractmethod
    def _get_finish_auction_dto(
        transaction: Transaction,
        datasource: TzktDatasource,
    ) -> FinishAuctionDto:
        raise NotImplementedError

    @classmethod
    @final
    async def handle(
        cls,
        transaction: Transaction,
        datasource: TzktDatasource,
    ):
        dto = cls._get_finish_auction_dto(transaction, datasource)

        auction = (
            await AuctionModel.filter(
                network=datasource.network,
                platform=cls.platform,
                auction_id=dto.auction_id,
            )
            .order_by('-id')
            .first()
        )

        auction.last_updated_at = transaction.data.timestamp
        auction.ended_at = transaction.data.timestamp
        auction.ongoing = False
        auction.status = AuctionStatusEnum.FINISHED
        auction.save()

        await AuctionActivityModel.create(
            auction_id=auction.id,
            type=ActivityTypeEnum.AUCTION_FINISHED,
            network=datasource.network,
            platform=cls.platform,
            internal_auction_id=dto.auction_id,
            bid_value=auction.last_bid_amount,
            bid_bidder=auction.last_bid_bidder,
            date=transaction.data.timestamp,
            last_updated_at=transaction.data.timestamp,
            operation_level=transaction.data.level,
            operation_timestamp=transaction.data.timestamp,
            operation_hash=transaction.data.hash,
            operation_counter=transaction.data.counter,
            operation_nonce=transaction.data.nonce,
        )


class AbstractCancelAuctionEvent(EventInterface):
    @staticmethod
    @abstractmethod
    def _get_cancel_auction_dto(
        transaction: Transaction,
        datasource: TzktDatasource,
    ) -> FinishAuctionDto:
        raise NotImplementedError

    @classmethod
    @final
    async def handle(
        cls,
        transaction: Transaction,
        datasource: TzktDatasource,
    ):
        dto = cls._get_cancel_auction_dto(transaction, datasource)

        auction = (
            await AuctionModel.filter(
                network=datasource.network,
                platform=cls.platform,
                auction_id=dto.auction_id,
            )
            .order_by('-id')
            .first()
        )

        auction.last_updated_at = transaction.data.timestamp
        auction.ended_at = transaction.data.timestamp
        auction.ongoing = False
        auction.status = AuctionStatusEnum.CANCELLED
        auction.save()

        await AuctionActivityModel.create(
            auction_id=auction.id,
            type=ActivityTypeEnum.AUCTION_CANCEL,
            network=datasource.network,
            platform=cls.platform,
            internal_auction_id=dto.auction_id,
            bid_value=auction.last_bid_amount,
            bid_bidder=auction.last_bid_bidder,
            date=transaction.data.timestamp,
            last_updated_at=transaction.data.timestamp,
            operation_level=transaction.data.level,
            operation_timestamp=transaction.data.timestamp,
            operation_hash=transaction.data.hash,
            operation_counter=transaction.data.counter,
            operation_nonce=transaction.data.nonce,
        )
