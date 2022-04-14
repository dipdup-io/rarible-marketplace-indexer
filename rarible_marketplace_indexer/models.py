from enum import Enum
from typing import List
from typing import Optional

from tortoise import fields
from tortoise.backends.base.client import BaseDBAsyncClient
from tortoise.models import Model
from tortoise.signals import post_save

from rarible_marketplace_indexer.producer.const import KafkaTopic
from rarible_marketplace_indexer.producer.container import ProducerContainer
from rarible_marketplace_indexer.producer.helper import producer_send
from rarible_marketplace_indexer.types.rarible_api_objects.asset.enum import AssetClassEnum
from rarible_marketplace_indexer.types.tezos_objects.asset_value.asset_value import AssetValueField
from rarible_marketplace_indexer.types.tezos_objects.asset_value.xtz_value import XtzField
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import AccountAddressField
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OperationHashField


class OrderStatusEnum(Enum):
    ACTIVE: str = 'ACTIVE'
    FILLED: str = 'FILLED'
    HISTORICAL: str = 'HISTORICAL'
    INACTIVE: str = 'INACTIVE'
    CANCELLED: str = 'CANCELLED'


class ActivityTypeEnum(Enum):
    LIST: str = 'LIST'
    MATCH: str = 'SELL'
    CANCEL: str = 'CANCEL_LIST'


class PlatformEnum(Enum):
    HEN: str = 'Hen'
    OBJKT: str = 'Objkt'
    OBJKT_V2: str = 'Objkt_v2'
    RARIBLE: str = 'Rarible'


class Activity(Model):
    class Meta:
        table = 'marketplace_activity'

    id = fields.BigIntField(pk=True)
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


class Order(Model):
    class Meta:
        table = 'marketplace_order'

    id = fields.BigIntField(pk=True, generated=False)
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
