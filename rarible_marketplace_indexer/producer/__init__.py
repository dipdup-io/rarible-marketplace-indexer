from typing import Union

from dipdup.config import CustomConfig
from kafka import KafkaProducer


class ProducerContainer:
    __instance: Union[None, KafkaProducer] = None

    @classmethod
    def get_instance(cls) -> KafkaProducer:
        if not isinstance(cls.__instance, KafkaProducer):
            raise RuntimeError
        return cls.__instance

    @classmethod
    def create_instance(cls, config: CustomConfig) -> None:
        cls.__instance = KafkaProducer(
            bootstrap_servers=[config.kafka_address],  # noqa
            client_id=config.client_id,  # noqa
            retries=config.retries,  # noqa
        )
