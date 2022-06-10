import uuid
from enum import Enum
from typing import Any
from typing import List
from typing import Optional
from typing import TypeVar
from uuid import uuid5

from dipdup.models import Transaction
from tortoise import fields
from tortoise.backends.base.client import BaseDBAsyncClient
from tortoise.models import Model
from tortoise.signals import post_save

from rarible_marketplace_indexer.producer.helper import producer_send
from rarible_marketplace_indexer.types.rarible_api_objects.asset.enum import AssetClassEnum
from rarible_marketplace_indexer.types.tezos_objects.asset_value.asset_value import AssetValueField
from rarible_marketplace_indexer.types.tezos_objects.asset_value.xtz_value import XtzField
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import AccountAddressField
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OperationHashField

_StrEnumValue = TypeVar("_StrEnumValue")


class TransactionTypeEnum(str, Enum):
    SALE: _StrEnumValue = 'SALE'
    BID: _StrEnumValue = 'BID'
    FLOOR_BID: _StrEnumValue = 'FLOOR_BID'
    AUCTION: _StrEnumValue = 'AUCTION'


class OrderStatusEnum(str, Enum):
    ACTIVE: _StrEnumValue = 'ACTIVE'
    FILLED: _StrEnumValue = 'FILLED'
    HISTORICAL: _StrEnumValue = 'HISTORICAL'
    INACTIVE: _StrEnumValue = 'INACTIVE'
    CANCELLED: _StrEnumValue = 'CANCELLED'


class AuctionStatusEnum(str, Enum):
    ACTIVE: _StrEnumValue = 'ACTIVE'
    FINISHED: _StrEnumValue = 'FINISHED'
    INACTIVE: _StrEnumValue = 'INACTIVE'
    CANCELLED: _StrEnumValue = 'CANCELLED'


class ActivityTypeEnum(str, Enum):
    GET_BID: _StrEnumValue = 'GET_BID'
    GET_FLOOR_BID: _StrEnumValue = 'GET_FLOOR_BID'
    ORDER_LIST: _StrEnumValue = 'LIST'
    ORDER_MATCH: _StrEnumValue = 'SELL'
    ORDER_CANCEL: _StrEnumValue = 'CANCEL_LIST'
    CANCEL_BID: _StrEnumValue = 'CANCEL_BID'
    CANCEL_FLOOR_BID: _StrEnumValue = 'CANCEL_FLOOR_BID'
    MAKE_BID: _StrEnumValue = 'MAKE_BID'
    MAKE_FLOOR_BID: _StrEnumValue = 'MAKE_FLOOR_BID'
    TOKEN_MINT: _StrEnumValue = 'MINT'
    TOKEN_TRANSFER: _StrEnumValue = 'TRANSFER'
    TOKEN_BURN: _StrEnumValue = 'BURN'
    AUCTION_CREATED: _StrEnumValue = 'AUCTION_CREATED'
    AUCTION_STARTED: _StrEnumValue = 'AUCTION_STARTED'
    AUCTION_BID: _StrEnumValue = 'AUCTION_BID'
    AUCTION_CANCEL: _StrEnumValue = 'AUCTION_CANCEL'
    AUCTION_FINISHED: _StrEnumValue = 'AUCTION_FINISHED'
    AUCTION_ENDED: _StrEnumValue = 'AUCTION_ENDED'


class PlatformEnum(str, Enum):
    HEN: _StrEnumValue = 'Hen'
    OBJKT: _StrEnumValue = 'Objkt'
    OBJKT_V2: _StrEnumValue = 'Objkt_v2'
    RARIBLE: _StrEnumValue = 'Rarible'


class ActivityModel(Model):
    class Meta:
        table = 'marketplace_activity'

    _custom_generated_pk = True

    id = fields.UUIDField(pk=True, generated=False, required=True, default=None)
    order_id = fields.UUIDField(required=True, index=True)
    type = fields.CharEnumField(ActivityTypeEnum)
    network = fields.CharField(max_length=16)
    platform = fields.CharEnumField(PlatformEnum)
    internal_order_id = fields.CharField(max_length=32, index=True)
    maker = AccountAddressField(null=True)
    taker = AccountAddressField(null=True)
    sell_price = XtzField()
    make_asset_class = fields.CharEnumField(AssetClassEnum)
    make_contract = AccountAddressField(null=True)
    make_token_id = fields.TextField(null=True)
    make_value = AssetValueField()
    take_asset_class = fields.CharEnumField(AssetClassEnum, null=True)
    take_contract = AccountAddressField(null=True)
    take_token_id = fields.TextField(null=True)
    take_value = AssetValueField(null=True)

    operation_level = fields.IntField()
    operation_timestamp = fields.DatetimeField()
    operation_hash = OperationHashField()
    operation_counter = fields.IntField()
    operation_nonce = fields.IntField(null=True)

    def __init__(self, **kwargs: Any) -> None:
        try:
            kwargs['id'] = self.get_id(**kwargs)
        except TypeError:
            pass
        super().__init__(**kwargs)

    @staticmethod
    def get_id(operation_hash, operation_counter, operation_nonce, *args, **kwargs):
        assert operation_hash
        assert operation_counter

        oid = '.'.join(map(str, filter(bool, [operation_hash, operation_counter, operation_nonce])))
        return uuid5(namespace=uuid.NAMESPACE_OID, name=oid)

    def apply(self, transaction: Transaction):
        new_id = self.get_id(transaction.data.hash, transaction.data.counter, transaction.data.nonce)
        activity = self.clone(pk=new_id)

        activity.operation_level = transaction.data.level
        activity.operation_timestamp = transaction.data.timestamp
        activity.operation_hash = transaction.data.hash
        activity.operation_counter = transaction.data.counter
        activity.operation_nonce = transaction.data.nonce

        return activity


class OrderModel(Model):
    class Meta:
        table = 'marketplace_order'

    _custom_generated_pk = True

    id = fields.UUIDField(pk=True, generated=False, required=True)
    network = fields.CharField(max_length=16, index=True)
    fill = XtzField(default=0)
    platform = fields.CharEnumField(PlatformEnum, index=True)
    internal_order_id = fields.CharField(max_length=32, index=True)
    status = fields.CharEnumField(OrderStatusEnum, index=True)
    start_at = fields.DatetimeField()
    end_at = fields.DatetimeField(null=True)
    make_stock = AssetValueField()
    cancelled = fields.BooleanField(default=False)
    salt = fields.BigIntField()
    created_at = fields.DatetimeField(index=True)
    ended_at = fields.DatetimeField(null=True)
    last_updated_at = fields.DatetimeField(index=True)
    make_price = XtzField()
    maker = AccountAddressField()
    taker = AccountAddressField(null=True)
    make_asset_class = fields.CharEnumField(AssetClassEnum)
    make_contract = AccountAddressField(null=True)
    make_token_id = fields.TextField(null=True)
    make_value = AssetValueField()
    take_asset_class = fields.CharEnumField(AssetClassEnum, null=True)
    take_contract = AccountAddressField(null=True)
    take_token_id = fields.TextField(null=True)
    take_value = AssetValueField(null=True)

    def __init__(self, **kwargs: Any) -> None:
        try:
            kwargs['id'] = self.get_id(**kwargs)
        except TypeError:
            pass
        super().__init__(**kwargs)

    @staticmethod
    def get_id(network, platform, internal_order_id, maker, created_at, *args, **kwargs):
        assert network
        assert platform
        assert internal_order_id
        assert maker
        assert created_at

        oid = '.'.join(map(str, filter(bool, [network, platform, internal_order_id, maker, created_at])))
        return uuid5(namespace=uuid.NAMESPACE_OID, name=oid)


class AuctionModel(Model):
    class Meta:
        table = 'marketplace_auction'

    _custom_generated_pk = True

    id = fields.UUIDField(pk=True, generated=False, required=True)
    network = fields.CharField(max_length=16, index=True)
    platform = fields.CharEnumField(PlatformEnum, index=True)
    auction_id = fields.CharField(max_length=32, index=True)
    status = fields.CharEnumField(AuctionStatusEnum, index=True)
    start_at = fields.DatetimeField()
    ended_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(index=True)
    end_time = fields.DatetimeField(index=True, null=True)
    last_updated_at = fields.DatetimeField(index=True)
    ongoing = fields.BooleanField(default=False)
    seller = AccountAddressField()
    sell_asset_class = fields.CharEnumField(AssetClassEnum)
    sell_contract = AccountAddressField(null=True)
    sell_token_id = fields.TextField(null=True)
    sell_value = AssetValueField()
    buy_asset_class = fields.CharEnumField(AssetClassEnum, null=True)
    buy_contract = AccountAddressField(null=True)
    buy_token_id = fields.TextField(null=True)
    minimal_step = fields.IntField()
    minimal_price = fields.IntField()
    duration = fields.IntField()
    buy_price = fields.IntField()
    max_seller_fees = fields.IntField()
    last_bid_amount = fields.IntField(null=True)
    last_bid_bidder = AccountAddressField(null=True)
    last_bid_date = fields.DatetimeField(null=True)

    def __init__(self, **kwargs: Any) -> None:
        try:
            kwargs['id'] = self.get_id(**kwargs)
        except TypeError:
            pass
        super().__init__(**kwargs)

    @staticmethod
    def get_id(network, platform, auction_id, seller, created_at, *args, **kwargs):
        assert network
        assert platform
        assert auction_id
        assert seller
        assert created_at

        oid = '.'.join(map(str, filter(bool, [network, platform, auction_id, seller, created_at])))
        return uuid5(namespace=uuid.NAMESPACE_OID, name=oid)


class AuctionActivityModel(Model):
    class Meta:
        table = 'marketplace_auction_activity'

    _custom_generated_pk = True

    id = fields.UUIDField(pk=True, generated=False, required=True, default=None)
    auction_id = fields.UUIDField(required=True, index=True)
    type = fields.CharEnumField(ActivityTypeEnum)
    network = fields.CharField(max_length=16)
    platform = fields.CharEnumField(PlatformEnum)
    internal_auction_id = fields.CharField(max_length=32, index=True)
    bid_value = fields.IntField(null=True)
    bid_bidder = AccountAddressField(null=True)
    date = fields.DatetimeField()
    last_updated_at = fields.DatetimeField(index=True)
    operation_level = fields.IntField()
    operation_timestamp = fields.DatetimeField()
    operation_hash = OperationHashField()
    operation_counter = fields.IntField()
    operation_nonce = fields.IntField(null=True)

    def __init__(self, **kwargs: Any) -> None:
        try:
            kwargs['id'] = self.get_id(**kwargs)
        except TypeError:
            pass
        super().__init__(**kwargs)

    @staticmethod
    def get_id(type, operation_hash, operation_counter, operation_nonce, *args, **kwargs):
        assert operation_hash
        assert operation_counter

        oid = '.'.join(map(str, filter(bool, [type, operation_hash, operation_counter, operation_nonce])))
        return uuid5(namespace=uuid.NAMESPACE_OID, name=oid)

    def apply(self, transaction: Transaction):
        new_id = self.get_id(transaction.data.hash, transaction.data.counter, transaction.data.nonce)
        activity = self.clone(pk=new_id)

        activity.operation_level = transaction.data.level
        activity.operation_timestamp = transaction.data.timestamp
        activity.operation_hash = transaction.data.hash
        activity.operation_counter = transaction.data.counter
        activity.operation_nonce = transaction.data.nonce

        return activity


@post_save(OrderModel)
async def signal_order_post_save(
    sender: OrderModel,
    instance: OrderModel,
    created: bool,
    using_db: "Optional[BaseDBAsyncClient]",
    update_fields: List[str],
) -> None:
    from rarible_marketplace_indexer.types.rarible_api_objects.order.factory import RaribleApiOrderFactory

    await producer_send(RaribleApiOrderFactory.build(instance))


@post_save(ActivityModel)
async def signal_activity_post_save(
    sender: ActivityModel,
    instance: ActivityModel,
    created: bool,
    using_db: "Optional[BaseDBAsyncClient]",
    update_fields: List[str],
) -> None:
    from rarible_marketplace_indexer.types.rarible_api_objects.activity.order.factory import RaribleApiOrderActivityFactory

    await producer_send(RaribleApiOrderActivityFactory.build(instance))


@post_save(AuctionModel)
async def signal_auction_post_save(
    sender: AuctionModel,
    instance: AuctionModel,
    created: bool,
    using_db: "Optional[BaseDBAsyncClient]",
    update_fields: List[str],
) -> None:
    from rarible_marketplace_indexer.types.rarible_api_objects.auction.factory import RaribleApiAuctionFactory

    await producer_send(RaribleApiAuctionFactory.build(instance))


@post_save(AuctionActivityModel)
async def signal_auction_activity_post_save(
    sender: AuctionActivityModel,
    instance: AuctionActivityModel,
    created: bool,
    using_db: "Optional[BaseDBAsyncClient]",
    update_fields: List[str],
) -> None:
    from rarible_marketplace_indexer.types.rarible_api_objects.activity.auction.factory import RaribleApiAuctionActivityFactory

    await producer_send(RaribleApiAuctionActivityFactory.build(instance))
