from rarible_marketplace_indexer.producer.serializer import kafka_value_serializer
from rarible_marketplace_indexer.types.rarible_api_objects.auction.factory import RaribleApiAuctionFactory
from rarible_marketplace_indexer.types.rarible_api_objects.order.factory import RaribleApiOrderFactory
from tests.models.conftest import compare_kafka_messages


class TestRaribleApiOrder:
    def test_kafka_topic(self, auction_data_provider):
        auction_api_object = RaribleApiAuctionFactory.build(auction_data_provider.test_model)
        assert auction_api_object.kafka_topic == 'auction_topic_ithacanet'

    def test_factory(self, auction_data_provider):
        auction_api_object = RaribleApiAuctionFactory.build(auction_data_provider.test_model)
        expected_object = auction_data_provider.test_api_object
        assert auction_api_object == expected_object

    def test_serializer(self, auction_data_provider):
        auction_message = kafka_value_serializer(auction_data_provider.test_api_object, sort_keys=True)
        expected_message = auction_data_provider.test_message
        compare_kafka_messages(auction_message, expected_message)
