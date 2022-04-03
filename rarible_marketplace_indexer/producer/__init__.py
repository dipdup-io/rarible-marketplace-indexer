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
        if config.enabled != 'false':  # noqa
            producer = KafkaProducer(
                bootstrap_servers=[config.kafka_address],  # noqa
                client_id=config.client_id,  # noqa
                retries=config.retries,  # noqa
                security_protocol=config.kafka_security_protocol,  # noqa
                sasl_mechanism=config.sasl['mechanism'],  # noqa
                sasl_plain_username=config.sasl['username'],  # noqa
                sasl_plain_password=config.sasl['password'],  # noqa
            )
        else:
            producer = NullKafkaProducer()

        cls.__instance = producer


# noinspection PyMissingConstructor
class NullKafkaProducer(KafkaProducer):
    def __init__(self, **configs):
        pass

    def send(self, *args, **kwargs):
        pass
