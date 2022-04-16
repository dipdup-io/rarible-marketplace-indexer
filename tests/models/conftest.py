from datetime import datetime

import pytest

from rarible_marketplace_indexer.models import Activity
from rarible_marketplace_indexer.models import ActivityTypeEnum
from rarible_marketplace_indexer.models import Order
from rarible_marketplace_indexer.models import OrderStatusEnum
from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.types.tezos_objects.asset_value.xtz_value import Xtz


@pytest.fixture
def listed_order_model():
    return Order(
        id=170668029,
        network='mainnet',
        fill=Xtz(0),
        platform=PlatformEnum.OBJKT_V2,
        internal_order_id=145,
        status=OrderStatusEnum.ACTIVE,
        started_at=datetime.now(),
        ended_at=None,
        make_stock=10,
        cancelled=False,
        salt=15958354,
        created_at=datetime.now(),
        last_updated_at=datetime.now(),
        make_price=Xtz(0.01),
        maker='tz1XHhjLXQuG9rf9n7o1VbgegMkiggy1oktu',
        taker=None,
        make_asset_class='TEZOS_FT',
        make_contract='KT1Q8JB2bdphCHhEBKc1PMsjArLPcAezGBVK',
        make_token_id=2,
        make_value=10,
    )


@pytest.fixture
def activity_model():
    return Activity(
        id=170668029,
        network='mainnet',
        platform=PlatformEnum.OBJKT_V2,
        type=ActivityTypeEnum.LIST,
        internal_order_id=145,
        maker='tz1XHhjLXQuG9rf9n7o1VbgegMkiggy1oktu',
        taker=None,
        sell_price=Xtz(0.01),
        make_asset_class='TEZOS_FT',
        make_contract='KT1Q8JB2bdphCHhEBKc1PMsjArLPcAezGBVK',
        make_token_id=2,
        make_value=10,
        operation_level=127001,
        operation_timestamp=datetime.now(),
        operation_hash='onh3uqBpi6cxfAiWzSxikskaUpwGTUQf6uQBFncwBQE9m5GMJLB',
    )
