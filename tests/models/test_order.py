from rarible_marketplace_indexer.producer.serializer import kafka_value_serializer
from rarible_marketplace_indexer.types.rarible_api_objects.order.factory import OrderFactory


class TestRaribleApiOrder:
    def test_serializer(self, listed_order_model):
        order_api_object = OrderFactory.build(listed_order_model)
        assert order_api_object.id == '170668029'
        order_message = kafka_value_serializer(order_api_object)
        assert (
            b'"make": {"assetType": {"assetClass": "TEZOS_FT", "contract": "KT1Q8JB2bdphCHhEBKc1PMsjArLPcAezGBVK", "tokenId": "2"}, "assetValue": 10}'
            in order_message
        )

    def test_kafka_topic(self, listed_order_model):
        order_api_object = OrderFactory.build(listed_order_model)
        assert order_api_object.kafka_topic == 'order_topic_mainnet'
