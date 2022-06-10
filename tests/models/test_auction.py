from rarible_marketplace_indexer.producer.serializer import kafka_value_serializer
from rarible_marketplace_indexer.types.rarible_api_objects.order.factory import RaribleApiOrderFactory
from tests.models.conftest import compare_kafka_messages


class TestRaribleApiOrder:
    def test_kafka_topic(self, order_data_provider):
        order_api_object = RaribleApiOrderFactory.build(order_data_provider.test_model)
        assert order_api_object.kafka_topic == 'order_topic_mainnet'

    def test_factory(self, order_data_provider):
        order_api_object = RaribleApiOrderFactory.build(order_data_provider.test_model)
        expected_object = order_data_provider.test_api_object
        assert order_api_object == expected_object

    def test_serializer(self, order_data_provider):
        order_message = kafka_value_serializer(order_data_provider.test_api_object, sort_keys=True)
        expected_message = order_data_provider.test_message
        compare_kafka_messages(order_message, expected_message)
