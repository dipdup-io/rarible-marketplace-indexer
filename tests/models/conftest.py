import json
from dataclasses import dataclass
from datetime import datetime
from importlib import import_module
from os import DirEntry
from os import scandir
from os.path import dirname
from os.path import join
from typing import Optional
from typing import Sequence

import pytest

from rarible_marketplace_indexer.models import Activity
from rarible_marketplace_indexer.models import ActivityTypeEnum
from rarible_marketplace_indexer.models import Order
from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.types.rarible_api_objects.order.order import RaribleApiOrder
from rarible_marketplace_indexer.types.tezos_objects.asset_value.xtz_value import Xtz


@dataclass
class TestOrderData:
    model: Order
    object: RaribleApiOrder
    message: Optional[bytes] = None


@pytest.fixture
def order_data_provider():
    order_module = 'tests.models.fixture_data.order'
    order_path_parts = [dirname(__file__), 'fixture_data/order']
    model_dir = join(*order_path_parts, 'model')  # noqa
    message_dir = join(*order_path_parts, 'message')  # noqa
    with scandir(model_dir) as entries:
        entries: Sequence[DirEntry]
        for entry in entries:
            if entry.name[:2] == '__':
                continue
            data_name = entry.name[:-3]
            module = import_module(f'{order_module}.model.{data_name}')
            order_model = module.order_model  # noqa
            del module
            module = import_module(f'{order_module}.object.{data_name}')
            order_object = module.order_object  # noqa
            del module
            with open(join(message_dir, f'{data_name}.json'), mode='r') as fp:
                order_message = json.dumps(json.load(fp), sort_keys=True, indent=2).encode()

            yield TestOrderData(model=order_model, object=order_object, message=order_message)


@pytest.fixture
def activity_model():
    return Activity(
        type=ActivityTypeEnum.LIST,
        network='mainnet',
        platform=PlatformEnum.OBJKT_V2,
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
        operation_counter=30182030,
        operation_nonce=1,
    )
