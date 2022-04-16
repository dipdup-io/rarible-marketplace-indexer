from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from rarible_marketplace_indexer.producer.serializer import kafka_value_serializer
from rarible_marketplace_indexer.types.rarible_api_objects.activity.factory import ActivityFactory


class TestRaribleApiActivity:
    def test_serializer(self, activity_model):
        activity_api_object = ActivityFactory.build(activity_model)

        assert activity_model.operation_hash
        assert activity_model.operation_counter

        assert str(activity_api_object.id) == 'ddce61de-326e-54d2-a91a-2d6fd2aa1d80'

        activity_message = kafka_value_serializer(activity_api_object)
        assert (
                b'"make": {"assetType": {"assetClass": "TEZOS_FT", "contract": "KT1Q8JB2bdphCHhEBKc1PMsjArLPcAezGBVK", "tokenId": "2"}, "assetValue": 10}'
                in activity_message
        )

    def test_clone(self, activity_model):
        old_id = activity_model.id

        @dataclass
        class TestOperationData:
            level: int
            timestamp: datetime
            hash: str
            counter: int
            nonce: Optional[int] = None

        @dataclass
        class TestTransaction:
            data: TestOperationData

        transaction = TestTransaction(
            data=TestOperationData(
                level=127009,
                timestamp=datetime.now(),
                hash='op25P9EWpUQiuvm4tbHjvqtUm674S1owiptFCskMh9r3oVmkinS',
                counter=30182030,
                nonce=3,
            )
        )
        new_activity_model = activity_model.apply(transaction)

        new_id = new_activity_model.id

        assert old_id != new_id
        assert isinstance(new_id, UUID)

    def test_kafka_topic(self, activity_model):
        activity_api_object = ActivityFactory.build(activity_model)
        assert activity_api_object.kafka_topic == 'activity_topic_mainnet'
