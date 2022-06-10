import json
from dataclasses import dataclass
from importlib import import_module
from os import DirEntry
from os import scandir
from os.path import dirname
from os.path import join
from typing import Dict
from typing import Optional
from typing import Sequence
from typing import Type

import pytest
from _pytest.fixtures import SubRequest
from pydantic import BaseModel
from tortoise.models import Model

from rarible_marketplace_indexer.models import ActivityModel, AuctionModel
from rarible_marketplace_indexer.models import AuctionActivityModel
from rarible_marketplace_indexer.models import OrderModel
from rarible_marketplace_indexer.types.rarible_api_objects.activity.auction.activity import RaribleApiAuctionActivity
from rarible_marketplace_indexer.types.rarible_api_objects.activity.order.activity import RaribleApiOrderActivity
from rarible_marketplace_indexer.types.rarible_api_objects.auction.auction import RaribleApiAuction
from rarible_marketplace_indexer.types.rarible_api_objects.order.order import RaribleApiOrder


class TestingSubject:
    order: str = 'order'
    activity: str = 'activity'
    auction: str = 'auction'
    auction_activity: str = 'auction_activity'


@dataclass
class TestModelData:
    test_model: Optional[Model]
    test_api_object: BaseModel
    test_message: Optional[bytes]


class TestOrderData(TestModelData):
    test_model: Optional[OrderModel]
    test_api_object: RaribleApiOrder


class TestActivityData(TestModelData):
    test_model: Optional[ActivityModel]
    test_api_object: RaribleApiOrderActivity


class TestAuctionData(TestModelData):
    test_model: Optional[AuctionModel]
    test_api_object: RaribleApiAuction


class TestAuctionActivityData(TestModelData):
    test_model: Optional[AuctionActivityModel]
    test_api_object: RaribleApiAuctionActivity


def import_object(object_name: str, object_type: str, testcase_name: str):
    try:
        test_module = import_module(f'tests.models.fixture_data.{object_name}.{object_type}.{testcase_name}')
        result = getattr(test_module, f'{object_name}_{object_type}')
        del test_module
    except ImportError:
        result = None

    return result


def data_loader(object_type: str):
    fixtures: Dict[str, Type[TestModelData]] = {
        TestingSubject.order: TestOrderData,
        TestingSubject.activity: TestActivityData,
        TestingSubject.auction: TestAuctionData,
        TestingSubject.auction_activity: TestAuctionActivityData,
    }

    object_dataclass = fixtures[object_type]

    object_path_parts = [dirname(__file__), f'fixture_data/{object_type}']
    model_dir = join(*object_path_parts, 'model')  # noqa
    message_dir = join(*object_path_parts, 'message')  # noqa
    with scandir(message_dir) as entries:
        entries: Sequence[DirEntry]
        for entry in entries:
            if entry.name[:2] == '__':
                continue
            datafile_basename = entry.name[:-5]

            test_model: Optional[Model] = import_object(object_type, 'model', datafile_basename)
            test_api_object = import_object(object_type, 'api_object', datafile_basename)

            with open(join(message_dir, f'{datafile_basename}.json'), mode='r') as fp:
                test_message = json.dumps(json.load(fp), sort_keys=True).encode()

            yield object_dataclass(test_model=test_model, test_api_object=test_api_object, test_message=test_message)  # noqa


@pytest.fixture(params=data_loader(TestingSubject.order))
def order_data_provider(request: SubRequest):
    return request.param


@pytest.fixture(params=filter(lambda x: x.test_model is not None, data_loader(TestingSubject.activity)))
def activity_model_data_provider(request: SubRequest):
    return request.param


@pytest.fixture(params=data_loader(TestingSubject.activity))
def activity_serializer_data_provider(request: SubRequest):
    return request.param


@pytest.fixture(params=data_loader(TestingSubject.auction))
def auction_data_provider(request: SubRequest):
    return request.param


@pytest.fixture(params=data_loader(TestingSubject.auction_activity))
def auction_activity_data_provider(request: SubRequest):
    return request.param


def compare_kafka_messages(actual: bytes, expected: bytes):
    assert type(actual) == type(expected) == bytes

    actual_dict: dict = json.loads(actual)
    expected_dict: dict = json.loads(expected)
    assert actual_dict.keys() == expected_dict.keys()

    assert actual_dict == expected_dict
