from rarible_marketplace_indexer.producer.serializer import kafka_value_serializer
from rarible_marketplace_indexer.types.rarible_api_objects.activity.factory import ActivityFactory


class TestRaribleApiActivity:
    def test_serializer(self, activity_model):
        activity_api_object = ActivityFactory.build(activity_model)
        assert activity_api_object.id == '170668029'
        activity_message = kafka_value_serializer(activity_api_object)
        assert (
            b'"make": {"assetType": {"assetClass": "TEZOS_FT", "contract": "KT1Q8JB2bdphCHhEBKc1PMsjArLPcAezGBVK", "tokenId": "2"}, "assetValue": 10}'
            in activity_message
        )

    def test_clone(self, activity_model):
        old_id = activity_model.id
        new_activity_model = activity_model.clone(pk=old_id + 1)
        new_id = new_activity_model.id

        assert old_id != new_id

    def test_kafka_topic(self, activity_model):
        activity_api_object = ActivityFactory.build(activity_model)
        assert activity_api_object.kafka_topic == 'activity_topic_mainnet'
