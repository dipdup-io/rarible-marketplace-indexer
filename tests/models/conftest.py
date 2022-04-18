import json
from abc import ABC
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
from pydantic import BaseModel
from tortoise.models import Model

from rarible_marketplace_indexer.models import Activity
from rarible_marketplace_indexer.models import Order
from rarible_marketplace_indexer.types.rarible_api_objects.activity.activity import RaribleApiActivity
from rarible_marketplace_indexer.types.rarible_api_objects.order.order import RaribleApiOrder


@dataclass
class TestModelData(ABC):
    test_model: Model = ...
    test_object: BaseModel = ...
    test_message: Optional[bytes] = None


class TestOrderData(TestModelData):
    test_model: Order
    test_object: RaribleApiOrder


class TestActivityData(TestModelData):
    test_model: Activity
    test_object: RaribleApiActivity


# @pytest.fixture(scope='function')
def data_loader(object_name):
    fixtures: Dict[str, Type[TestModelData]] = {
        'order': TestOrderData,
        'activity': TestActivityData,
    }

    object_dataclass = fixtures[object_name]

    object_module = f'tests.models.fixture_data.{object_name}'
    object_path_parts = [dirname(__file__), f'fixture_data/{object_name}']
    model_dir = join(*object_path_parts, 'model')  # noqa
    message_dir = join(*object_path_parts, 'message')  # noqa
    with scandir(model_dir) as entries:
        entries: Sequence[DirEntry]
        for entry in entries:
            if entry.name[:2] == '__':
                continue
            datafile_basename = entry.name[:-3]
            module = import_module(f'{object_module}.model.{datafile_basename}')
            test_model: Model = getattr(module, f'{object_name}_model')  # noqa
            del module
            module = import_module(f'{object_module}.object.{datafile_basename}')
            test_object = getattr(module, f'{object_name}_object')  # noqa
            del module
            with open(join(message_dir, f'{datafile_basename}.json'), mode='r') as fp:
                test_message = json.dumps(json.load(fp), sort_keys=True, indent=2).encode()

                yield object_dataclass(test_model=test_model, test_object=test_object, test_message=test_message)


@pytest.fixture
def order_data_provider():
    for test_data in data_loader('order'):
        yield test_data


@pytest.fixture
def activity_data_provider():
    for test_data in data_loader('activity'):
        yield test_data
