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


class OrderStatusEnum(str, Enum):
    ACTIVE: _StrEnumValue = 'ACTIVE'
    FILLED: _StrEnumValue = 'FILLED'
    HISTORICAL: _StrEnumValue = 'HISTORICAL'
    INACTIVE: _StrEnumValue = 'INACTIVE'
    CANCELLED: _StrEnumValue = 'CANCELLED'


class ActivityTypeEnum(str, Enum):
    LIST: _StrEnumValue = 'LIST'
    MATCH: _StrEnumValue = 'SELL'
    CANCEL: _StrEnumValue = 'CANCEL_LIST'


class PlatformEnum(str, Enum):
    HEN: _StrEnumValue = 'Hen'
    OBJKT: _StrEnumValue = 'Objkt'
    OBJKT_V2: _StrEnumValue = 'Objkt_v2'
    RARIBLE: _StrEnumValue = 'Rarible'


class Activity(Model):
    class Meta:
        table = 'marketplace_activity'

    _custom_generated_pk = True

    id = fields.UUIDField(pk=True, generated=False, required=True, default=None)
    order_id = fields.UUIDField(required=True, index=True)
    type = fields.CharEnumField(ActivityTypeEnum)
    network = fields.CharField(max_length=16)
    platform = fields.CharEnumField(PlatformEnum)
    internal_order_id = fields.CharField(max_length=32, index=True)
    maker = AccountAddressField()
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


class Order(Model):
    class Meta:
        table = 'marketplace_order'

    _custom_generated_pk = True

    id = fields.UUIDField(pk=True, generated=False, required=True)
    network = fields.CharField(max_length=16, index=True)
    fill = XtzField(default=0)
    platform = fields.CharEnumField(PlatformEnum, index=True)
    internal_order_id = fields.CharField(max_length=32, index=True)
    status = fields.CharEnumField(OrderStatusEnum, index=True)
    started_at = fields.DatetimeField()
    ended_at = fields.DatetimeField(null=True)
    make_stock = AssetValueField()
    cancelled = fields.BooleanField(default=False)
    salt = fields.BigIntField()
    created_at = fields.DatetimeField(index=True)
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
    def get_id(network, platform, internal_order_id, *args, **kwargs):
        assert network
        assert platform
        assert internal_order_id

        oid = '.'.join(map(str, filter(bool, [network, platform, internal_order_id])))
        return uuid5(namespace=uuid.NAMESPACE_OID, name=oid)


@post_save(Order)
async def signal_order_post_save(
    sender: Order,
    instance: Order,
    created: bool,
    using_db: "Optional[BaseDBAsyncClient]",
    update_fields: List[str],
) -> None:
    from rarible_marketplace_indexer.types.rarible_api_objects.order.factory import OrderFactory

    await producer_send(OrderFactory.build(instance))


@post_save(Activity)
async def signal_activity_post_save(
    sender: Activity,
    instance: Activity,
    created: bool,
    using_db: "Optional[BaseDBAsyncClient]",
    update_fields: List[str],
) -> None:
    from rarible_marketplace_indexer.types.rarible_api_objects.activity.factory import ActivityFactory

    await producer_send(ActivityFactory.build(instance))
