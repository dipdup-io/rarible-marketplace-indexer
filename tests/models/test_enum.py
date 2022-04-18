import pytest

from rarible_marketplace_indexer.models import ActivityTypeEnum
from rarible_marketplace_indexer.models import OrderStatusEnum
from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.models import _StrEnumValue  # noqa


class TestStrEnum:
    @pytest.mark.parametrize(
        'enum_class, enum_field, enum_value',
        (
            [OrderStatusEnum, OrderStatusEnum.ACTIVE, 'ACTIVE'],
            [OrderStatusEnum, OrderStatusEnum.FILLED, 'FILLED'],
            [OrderStatusEnum, OrderStatusEnum.HISTORICAL, 'HISTORICAL'],
            [OrderStatusEnum, OrderStatusEnum.INACTIVE, 'INACTIVE'],
            [OrderStatusEnum, OrderStatusEnum.CANCELLED, 'CANCELLED'],
            [ActivityTypeEnum, ActivityTypeEnum.LIST, 'LIST'],
            [ActivityTypeEnum, ActivityTypeEnum.MATCH, 'SELL'],
            [ActivityTypeEnum, ActivityTypeEnum.CANCEL, 'CANCEL_LIST'],
            [PlatformEnum, PlatformEnum.HEN, 'Hen'],
            [PlatformEnum, PlatformEnum.OBJKT, 'Objkt'],
            [PlatformEnum, PlatformEnum.OBJKT_V2, 'Objkt_v2'],
            [PlatformEnum, PlatformEnum.RARIBLE, 'Rarible'],
        ),
    )
    def test_enum(self, enum_class, enum_field, enum_value):
        assert enum_field == enum_value
        assert enum_field.value == enum_value  # noqa
        assert isinstance(enum_field, enum_class)  # noqa
