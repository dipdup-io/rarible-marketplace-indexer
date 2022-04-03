from enum import Enum
from typing import List
from typing import Optional

from tortoise import BaseDBAsyncClient
from tortoise import Model
from tortoise import fields
from tortoise.signals import post_save

from rarible_marketplace_indexer.const import KafkaTopic
from rarible_marketplace_indexer.producer import ProducerContainer
from rarible_marketplace_indexer.types.tezos_objects.tezos_currency import AssetValueField
from rarible_marketplace_indexer.types.tezos_objects.tezos_currency import XtzField
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import AccountAddressField
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OperationHashField


class StatusEnum(Enum):
    ACTIVE: str = 'ACTIVE'
    FILLED: str = 'FILLED'
    HISTORICAL: str = 'HISTORICAL'
    INACTIVE: str = 'INACTIVE'
    CANCELLED: str = 'CANCELLED'


class ActivityTypeEnum(Enum):
    LIST: str = 'list'
    CANCEL: str = 'cancel'
    MATCH: str = 'match'


class PlatformEnum(Enum):
    HEN: str = 'Hen'
    OBJKT: str = 'Objkt'
    OBJKT_V2: str = 'Objkt_v2'
    RARIBLE: str = 'Rarible'


class Activity(Model):
    id = fields.BigIntField(pk=True)
    type = fields.CharEnumField(ActivityTypeEnum)
    network = fields.CharField(max_length=16)
    platform = fields.CharEnumField(PlatformEnum)
    internal_order_id = fields.CharField(max_length=32, index=True)
    maker = AccountAddressField()
    taker = AccountAddressField(null=True)
    contract = AccountAddressField()
    token_id = fields.TextField()
    amount = AssetValueField()
    sell_price = XtzField()
    operation_level = fields.IntField()
    operation_timestamp = fields.DatetimeField()
    operation_hash = OperationHashField()

    class Meta:
        table = 'marketplace_activity'


class Order(Model):
    id = fields.BigIntField(pk=True)
    network = fields.CharField(max_length=16, index=True)
    fill = XtzField(default=0)
    platform = fields.CharEnumField(PlatformEnum, index=True)
    internal_order_id = fields.CharField(max_length=32, index=True)
    status = fields.CharEnumField(StatusEnum, index=True)
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
    make_contract = AccountAddressField()
    make_token_id = fields.TextField()
    make_value = AssetValueField()

    class Meta:
        table = 'marketplace_order'
        # unique_together = (("network", "contract", "token_id", "seller"),)


@post_save(Order)
async def signal_order_post_save(
    sender: Order,
    instance: Order,
    created: bool,
    using_db: "Optional[BaseDBAsyncClient]",
    update_fields: List[str],
) -> None:
    from rarible_marketplace_indexer.types.rarible_api_objects.api_order import OrderFactory

    producer = ProducerContainer.get_instance()
    producer.send(
        topic=KafkaTopic.ORDER_TOPIC,
        value=OrderFactory.for_kafka(instance),
    )


@post_save(Activity)
async def signal_activity_post_save(
    sender: Activity,
    instance: Activity,
    created: bool,
    using_db: "Optional[BaseDBAsyncClient]",
    update_fields: List[str],
) -> None:
    from rarible_marketplace_indexer.types.rarible_api_objects.api_activity import ActivityFactory

    producer = ProducerContainer.get_instance()
    producer.send(
        topic=KafkaTopic.ACTIVITY_TOPIC,
        value=ActivityFactory.for_kafka(instance),
    )
