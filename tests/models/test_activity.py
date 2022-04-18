from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from rarible_marketplace_indexer.producer.serializer import kafka_value_serializer
from rarible_marketplace_indexer.types.rarible_api_objects.activity.factory import ActivityFactory


class TestRaribleApiActivity:
    def test_kafka_topic(self, activity_data_provider):
        activity_api_object = ActivityFactory.build(activity_data_provider.test_model)
        assert activity_api_object.kafka_topic == 'activity_topic_mainnet'

    def test_factory(self, activity_data_provider):
        activity_api_object = ActivityFactory.build(activity_data_provider.test_model)
        expected_object = activity_data_provider.test_object
        assert activity_api_object == expected_object

    def test_serializer(self, activity_data_provider):
        activity_message = kafka_value_serializer(activity_data_provider.test_object, indent=2, sort_keys=True)
        expected_message = activity_data_provider.test_message
        assert activity_message == expected_message

    def test_clone(self, activity_data_provider):
        activity_model = activity_data_provider.test_model
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
