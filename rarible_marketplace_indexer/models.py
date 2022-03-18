from enum import Enum
from typing import List
from typing import Optional

from tortoise import BaseDBAsyncClient
from tortoise import Model
from tortoise import fields
from tortoise.signals import post_save


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
    id = fields.IntField(pk=True)
    type = fields.CharEnumField(ActivityTypeEnum)
    network = fields.CharField(max_length=16)
    platform = fields.CharEnumField(PlatformEnum)
    internal_order_id = fields.IntField()
    maker = fields.CharField(max_length=36)
    contract = fields.CharField(max_length=36)
    token_id = fields.CharField(max_length=16)
    amount = fields.CharField(max_length=16)
    sell_price = fields.CharField(max_length=16)
    action_level = fields.IntField()
    action_timestamp = fields.DatetimeField()

    class Meta:
        table = 'marketplace_activity'


class Order(Model):
    id = fields.IntField(pk=True)
    network = fields.CharField(max_length=16)
    fill = fields.CharField(max_length=16, null=True)
    platform = fields.CharEnumField(PlatformEnum)
    internal_order_id = fields.IntField(index=True)
    status = fields.CharEnumField(StatusEnum)
    started_at = fields.DatetimeField()
    ended_at = fields.DatetimeField(null=True)
    cancelled = fields.BooleanField()
    created_at = fields.DatetimeField(index=True)
    last_updated_at = fields.DatetimeField(index=True)
    make_price = fields.CharField(max_length=16)
    maker = fields.CharField(max_length=36)
    make_contract = fields.CharField(max_length=36)
    make_token_id = fields.CharField(max_length=16)
    make_amount = fields.CharField(max_length=16)

    class Meta:
        table = 'marketplace_order'
        # unique_together = (("network", "contract", "token_id", "seller"),)


@post_save(Order)
async def signal_post_save(
    sender: Order,
    instance: Order,
    created: bool,
    using_db: "Optional[BaseDBAsyncClient]",
    update_fields: List[str],
) -> None:
    # producer.send()
    pass
