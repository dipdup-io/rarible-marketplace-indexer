from typing import Any
from typing import Dict
from typing import Union

from kafka import KafkaProducer


class ProducerContainer:
    __instance: Union[None, KafkaProducer] = None

    @classmethod
    def get_instance(cls) -> KafkaProducer:
        if not isinstance(cls.__instance, KafkaProducer):
            raise RuntimeError
        return cls.__instance

    @classmethod
    def create_instance(cls, config: Dict[str, Any]) -> None:
        if config['enabled'] != 'false':
            producer = KafkaProducer(
                bootstrap_servers=[config['kafka_address']],
                client_id=config['client_id'],
                retries=config['retries'],
                security_protocol=config['kafka_security_protocol'],
                sasl_mechanism=config['sasl']['mechanism'],
                sasl_plain_username=config['sasl']['username'],
                sasl_plain_password=config['sasl']['password'],
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
